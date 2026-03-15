from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from supabase import create_client, Client as SupabaseClient

from core.database import get_db
from core.config import settings
from api.deps import get_current_user
from models.user import User
from models.client import Client
from schemas.client import ClientResponse, ClientCreate, ClientBase, ClientUpdate

router = APIRouter()

# Initialize Supabase client
supabase: SupabaseClient = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@router.get("/supabase", response_model=List[dict])
def get_supabase_clients(
    localidade: str = None,
    categoria: str = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Fetch clients from Supabase (table 'places') with optional filters.
    """
    try:
        # Based on the user's provided schema image, the table is called 'places'
        query = supabase.table("places").select("*")
        if localidade:
            query = query.ilike("cidade", f"%{localidade}%")
        if categoria:
            query = query.ilike("categoria", f"%{categoria}%")
            
        response = query.limit(100).execute()
        
        # Map Supabase columns to our local schema
        mapped_data = []
        for item in response.data:
            mapped_data.append({
                "id": item.get("id"),
                "telefone": item.get("numero_telefone") or item.get("phone") or "N/A",
                "localidade": item.get("cidade") or item.get("location") or "",
                "categoria": item.get("categoria") or "",
                "categoria_especifica": item.get("termo_buscado") or "", # using termo_buscado as specific
                "nome": item.get("nome")
            })
        return mapped_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from Supabase: {str(e)}")

@router.get("/supabase-filters")
def get_supabase_filters(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get unique cities and categories from the Supabase 'places' table for autocomplete.
    """
    try:
        # Fetching a sample to extract unique values (Supabase doesn't have a direct 'DISTINCT' via API easily for multiple columns)
        # We can perform a query for unique values if we use RPC, but for now let's do a select of specific columns
        cities_res = supabase.table("places").select("cidade").execute()
        cats_res = supabase.table("places").select("categoria").execute()
        
        cities = sorted(list(set([item['cidade'] for item in cities_res.data if item.get('cidade')])))
        categories = sorted(list(set([item['categoria'] for item in cats_res.data if item.get('categoria')])))
        
        return {
            "cidades": cities,
            "categorias": categories
        }
    except Exception as e:
        print(f"Filter fetch error: {e}")
        return {"cidades": [], "categorias": []}


@router.post("/import", response_model=List[ClientResponse])
def import_clients(
    clients_in: List[ClientCreate],
    base_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Import selected clients into a specific Client Base.
    """
    imported_clients = []
    
    for client_data in clients_in:
        # Check if already imported in THIS base
        existing = db.query(Client).filter(
            Client.telefone == client_data.telefone,
            Client.owner_id == current_user.id,
            Client.base_id == base_id
        ).first()
        
        if not existing:
            new_client = Client(
                telefone=client_data.telefone,
                localidade=client_data.localidade,
                categoria=client_data.categoria,
                categoria_especifica=client_data.categoria_especifica,
                status=client_data.status, # will default to cold lead if not provided
                owner_id=current_user.id,
                base_id=base_id
            )
            db.add(new_client)
            imported_clients.append(new_client)
            
    db.commit()
    for c in imported_clients:
        db.refresh(c)
        
    return imported_clients


@router.get("/", response_model=List[ClientResponse])
def get_my_clients(
    base_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve clients. If base_id is provided, filter by that base.
    """
    query = db.query(Client).filter(Client.owner_id == current_user.id)
    if base_id:
        query = query.filter(Client.base_id == base_id)
    return query.all()

@router.patch("/{client_id}", response_model=ClientResponse)
def update_client_status(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update client status (used for Drag and Drop).
    """
    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == current_user.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if client_update.status is not None:
        client.status = client_update.status
    
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

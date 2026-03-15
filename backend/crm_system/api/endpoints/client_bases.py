from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from api.deps import get_current_user
from models.user import User
from models.client_base import ClientBaseList
from schemas.client_base import ClientBaseListCreate, ClientBaseListResponse

router = APIRouter()

@router.get("/", response_model=List[ClientBaseListResponse])
def get_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all client bases for the current user.
    """
    return db.query(ClientBaseList).filter(ClientBaseList.owner_id == current_user.id).all()

@router.post("/", response_model=ClientBaseListResponse)
def create_base(
    *,
    db: Session = Depends(get_db),
    base_in: ClientBaseListCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new client base.
    """
    base = ClientBaseList(
        **base_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(base)
    db.commit()
    db.refresh(base)
    return base

@router.delete("/{base_id}")
def delete_base(
    *,
    db: Session = Depends(get_db),
    base_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a client base.
    """
    base = db.query(ClientBaseList).filter(
        ClientBaseList.id == base_id, 
        ClientBaseList.owner_id == current_user.id
    ).first()
    if not base:
        raise HTTPException(status_code=404, detail="Base not found")
    db.delete(base)
    db.commit()
    return {"status": "success"}

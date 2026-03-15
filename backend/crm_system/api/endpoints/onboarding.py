from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import re

from core.database import get_db
from api.deps import get_current_user
from models.user import User
from models.client import Client, ClientStatus
from models.client_base import ClientBaseList
from core.config import settings
from supabase import create_client, Client as SupabaseClient

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

router = APIRouter()

# Initialize Supabase client
supabase: SupabaseClient = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

SYSTEM_PROMPT = """Você é o ESPECIALISTA EM GROWTH (AGENTE 1). Seu objetivo é entrevistar o usuário para configurar seu CRM.

REGRAS CRÍTICAS:
1. NUNCA mostre o JSON, tags como [FINALIZAR] ou as 'query_instructions' para o usuário. 
2. Suas respostas devem ser 100% humanas, calorosas e profissionais.
3. Quando decidir finalizar, envie sua mensagem de encerramento humana e, SOMENTE DEPOIS dela, adicione a tag [FINALIZAR] e o JSON.

COMO FINALIZAR:
Finalize a conversa de forma natural. Ao final da última mensagem, anexe:
[FINALIZAR]
{
  "resumo": "Frase resumindo o negócio",
  "query_instructions": "Descrição detalhada do PÚBLICO ALVO e LOCALIDADE para o Agente 2."
}
"""

SEARCH_AGENT_PROMPT = """Você é o AGENTE DE BUSCA (AGENTE 2). Sua tarefa é transformar 'Instruções de Busca' em critérios técnicos precisos usando EXCLUSIVAMENTE os termos disponíveis no banco de dados.

O Agente 1 descreveu o público-alvo do usuário. Você deve mapear esse público para um ou mais dos "TERMOS DE BUSCA REAIS" listados abaixo.

TERMOS DE BUSCA REAIS (Disponíveis no banco):
- açaí, bar, barbearia, buffet, buffet infantil, cafeteria, churrascaria
- clínica de estética, clínica de fisioterapia, clínica médica, doceria
- esteticista, extensão de cílios, fisioterapeuta industrial, food truck
- ginecologista, hamburgueria, joalheria, lanchonete, limpeza a laser
- loja de acessórios, loja de bijuterias, loja de bolsas, loja de calçados
- loja feminina, loja infantil, loja masculina, manicure, marmitaria
- massoterapia, odontopediatra, ortodontista, padaria, pedicure, pizzaria
- podóloga, psicólogo, pub, restaurante, restaurante italiano, restaurante japonês
- restaurante vegetariano, restaurante árabe, salão de beleza, sorveteria, spa, steakhouse

REGRAS:
1. Use apenas os termos da lista acima no campo 'keywords'.
2. Analise o alvo do usuário: Se ele quer vender para "Sushis", use "restaurante japonês". Se quer vender para "Pizzarias", use "pizzaria".
3. Localidade deve ser extraída das instruções.

Instruções do Agente 1: {instructions}

Responda APENAS com um JSON puro:
{{
  "localidade": "Nome da Cidade",
  "keywords": ["termo_da_lista_1", "termo_da_lista_2"]
}}
"""

@router.post("/chat")
async def onboarding_chat(
    user_message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not settings.OPENAI_API_KEY:
        # Fallback for hackathon if no key is provided, just to show it works
        # But wait, I'll try to use the actual key if provided.
        # If not, I'll return a helpful error.
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY não encontrada no ambiente.")

    # Load history from user model
    history_data = []
    if current_user.onboarding_context:
        try:
            history_data = json.loads(current_user.onboarding_context)
        except:
            history_data = []

    history = []
    for msg in history_data:
        if msg['role'] == 'user':
            history.append(HumanMessage(content=msg['content']))
        else:
            history.append(AIMessage(content=msg['content']))

    try:
        llm = ChatOpenAI(model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY)
        
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + history + [HumanMessage(content=user_message)]
        
        response = llm.invoke(messages)
        ai_content = response.content
        print(f"DEBUG: AI Response: {ai_content}")

        # Save history
        history_data.append({"role": "user", "content": user_message})
        history_data.append({"role": "assistant", "content": ai_content})
        current_user.onboarding_context = json.dumps(history_data)
        db.add(current_user)
        db.commit()

        if "[FINALIZAR]" in ai_content.upper():
            print("DEBUG: Finalização detectada!")
            # Use regex to find [FINALIZAR] regardless of case
            parts = re.split(r"\[FINALIZAR\]", ai_content, flags=re.IGNORECASE)
            chat_response = parts[0].strip()
            data_json_raw = parts[1].strip()
            
            try:
                # Try to extract JSON from markdown if exists
                json_match = re.search(r"(\{.*\})", data_json_raw, re.DOTALL)
                if json_match:
                    data_json = json_match.group(1)
                else:
                    data_json = data_json_raw
                    
                print(f"DEBUG: JSON extraído: {data_json}")
                profile_data = json.loads(data_json)
                
                current_user.user_info = profile_data.get("resumo")
                
                # CRITICAL: Create the base IMMEDIATELY here to ensure it exists
                base = db.query(ClientBaseList).filter(
                    ClientBaseList.owner_id == current_user.id,
                    ClientBaseList.name == "Leads do Agente"
                ).first()
                
                if not base:
                    print("DEBUG: Criando banco 'Leads do Agente' no gatilho de finalização...")
                    base = ClientBaseList(
                        name="Leads do Agente", 
                        description=f"Leads capturados por IA para: {current_user.user_info}", 
                        owner_id=current_user.id
                    )
                    db.add(base)
                
                db.commit()
                db.refresh(current_user)
                
                # Extract search instructions for the second agent
                query_instructions = profile_data.get("query_instructions", "")
                
                # Call search agent in background or await it
                try:
                    await generate_cold_leads_multi_agent(current_user, query_instructions, db)
                except Exception as e_leads:
                    print(f"ERROR: Falha grave na prospecção: {e_leads}")
                
                return {
                    "message": chat_response or "Excelente! Seu CRM está sendo preparado agora.",
                    "is_complete": True,
                    "user_info": current_user.user_info
                }
            except Exception as e:
                print(f"ERROR: Falha no parsing do JSON final: {e}")
                # Even if JSON fails, if [FINALIZAR] was there, we try to mark as complete
                return {"message": chat_response or ai_content, "is_complete": True}

        return {"message": ai_content, "is_complete": False}
    except Exception as e:
        print(f"ERROR: Erro geral no onboarding: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no LLM: {str(e)}")

async def generate_cold_leads_multi_agent(user: User, query_instructions: str, db: Session):
    print(f"DEBUG: AGENTE 2 (BUSCA) interpretando instruções: {query_instructions[:50]}...")
    
    # AGENTE 2: Parsing instructions
    try:
        llm = ChatOpenAI(model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY)
        search_prompt = SEARCH_AGENT_PROMPT.format(instructions=query_instructions)
        
        response = llm.invoke([SystemMessage(content=search_prompt)])
        data_json_raw = response.content.strip()
        
        # Cleanup JSON from markdown
        json_match = re.search(r"(\{.*\})", data_json_raw, re.DOTALL)
        data_json = json_match.group(1) if json_match else data_json_raw
            
        search_params = json.loads(data_json)
        localidade = search_params.get("localidade")
        categorias = search_params.get("categorias", [])
        keywords = search_params.get("keywords", [])
        
        print(f"DEBUG: Critérios definidos: Loc={localidade}, Cats={categorias}, Kws={keywords}")
        
    except Exception as e:
        print(f"ERROR: Agente 2 falhou no parsing técnico: {e}")
        return

    # Find the base created in the previous step
    base = db.query(ClientBaseList).filter(
        ClientBaseList.owner_id == user.id,
        ClientBaseList.name == "Leads do Agente"
    ).first()
    
    if not base:
        print("ERROR: Banco 'Leads do Agente' não encontrado para o usuário.")
        return

    try:
        query = supabase.table("places").select("*")
        
        # 1. Location (Fundamental)
        loc_clean = localidade.strip() if localidade else ""
        if loc_clean:
            # The database uses 'São Paulo'. We try exact match first, then partial.
            # loc_match helps skip accent issues if needed
            loc_match = loc_clean.replace("São Paulo", "ão Paulo")
            query = query.ilike("cidade", f"%{loc_match}%")
        
        # 2. ULTRA-STRICT TARGETING: Match 'termo_buscado'
        if keywords:
            kw_conditions = []
            for kw in keywords:
                # ground truth
                kw_conditions.append(f"termo_buscado.ilike.%{kw}%")
            
            or_filter = ",".join(kw_conditions)
            query = query.or_(or_filter)
        
        print(f"DEBUG: Executando busca no Supabase para {loc_clean} com termos {keywords}")
        response = query.limit(100).execute()
        
        # If strict search returned nothing, try matching the keyword in the NAME instead of just category
        if not response.data and keywords:
            print("DEBUG: Nenhum match em 'termo_buscado'. Tentando match no NOME...")
            query_name = supabase.table("places").select("*")
            if localidade:
                query_name = query_name.ilike("cidade", f"%{loc_match}%")
            
            name_conditions = [f"nome.ilike.%{kw}%" for kw in keywords]
            query_name = query_name.or_(",".join(name_conditions))
            response = query_name.limit(50).execute()
        
        # NO BROAD FALLBACK here anymore to avoid "fish distributor getting non-japanese results"
        # The agent should only get what matches the criteria.

        print(f"DEBUG: Foram encontrados {len(response.data)} resultados no Supabase.")
        
        count = 0
        for item in response.data:
            nome = item.get("nome", "Empresa sem nome")
            tel = item.get("numero_telefone") or item.get("phone") or "N/A"
            
            # Uniqueness check: phone (if exists) OR name+location
            if tel != "N/A":
                existing = db.query(Client).filter(
                    Client.telefone == tel,
                    Client.owner_id == user.id,
                    Client.base_id == base.id
                ).first()
            else:
                existing = db.query(Client).filter(
                    Client.nome == nome,
                    Client.owner_id == user.id,
                    Client.base_id == base.id
                ).first()
            
            if not existing:
                new_client = Client(
                    nome=nome,
                    telefone=tel,
                    localidade=item.get("cidade") or item.get("estado") or "",
                    categoria=item.get("categoria") or "",
                    status=ClientStatus.COLD_LEAD,
                    owner_id=user.id,
                    base_id=base.id
                )
                db.add(new_client)
                count += 1
        
        db.commit()
        print(f"DEBUG: {count} novos leads adicionados com sucesso ao Kanban.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: Erro fatal no processamento dos dados do Agente 2: {str(e)}")

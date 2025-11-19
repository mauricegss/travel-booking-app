from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import time
import os

# --- Importações do LangGraph (Originais) ---
# Certifique-se de que o langgraph_app.py está correto e no mesmo diretório
from app.langgraph_app import app as langgraph_app, TravelAppState, FinalReport, CuratedRecommendation

# --- Novas Importações para Banco de Dados e Auth ---
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import User, Report
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

# Cria as tabelas no banco de dados (caso não existam)
Base.metadata.create_all(bind=engine)

# --- Modelos Pydantic para a API ---

class TripRequest(BaseModel):
    user_request: str

class TripDataResponse(BaseModel):
    final_report: FinalReport | None = Field(None)
    destination: str | None = Field(None)
    start_date: str | None = Field(None)
    end_date: str | None = Field(None)
    error: str | None = Field(None)

# Novos modelos para Auth e Relatórios
class UserCreate(BaseModel):
    email: str
    password: str

class ReportCreate(BaseModel):
    destination: str
    start_date: str
    end_date: str
    content: Dict[str, Any] # Recebe o JSON completo do relatório

# --- Configuração da App ---

api = FastAPI()

origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTAS DE AUTENTICAÇÃO (Novas) ---

@api.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verifica se usuário já existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Cria novo usuário
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "Usuário criado com sucesso"}

@api.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Busca usuário
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gera token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- ROTAS DE RELATÓRIOS (Novas) ---

@api.post("/reports")
def save_report(
    report_in: ReportCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    new_report = Report(
        user_id=current_user.id,
        destination=report_in.destination,
        start_date=report_in.start_date,
        end_date=report_in.end_date,
        content=report_in.content
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return {"id": new_report.id, "message": "Relatório salvo com sucesso!"}

@api.get("/reports")
def get_my_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Retorna apenas os relatórios do usuário logado
    return db.query(Report).filter(Report.user_id == current_user.id).all()

@api.delete("/reports/{report_id}")
def delete_report(
    report_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    
    db.delete(report)
    db.commit()
    return {"message": "Relatório apagado"}

# --- ROTA DE PLANEJAMENTO (Original) ---

@api.post("/plan-trip", response_model=TripDataResponse)
async def plan_trip(request: TripRequest):
    print("--- Endpoint /plan-trip ACESSADO ---")
    start_time = time.time()
    print(f"Recebido user_request: {request.user_request}")
    
    # O estado inicial agora usa os campos 'raw_'
    initial_state = TravelAppState(
        user_request=request.user_request,
        origin=None,
        destination=None,
        start_date=None,
        end_date=None,
        raw_flights=None,
        raw_hotels=None,
        raw_activities=None,
        final_report=None,
        error=None
    )
    
    try:
        print("Invocando app.invoke...")
        final_response_state = langgraph_app.invoke(initial_state)
        print("app.invoke concluído.")

        # Checa se houve um erro E NENHUM relatório foi gerado
        if final_response_state.get("error") and not final_response_state.get("final_report"):
             error_msg = final_response_state['error']
             print(f"Erro retornado pelo grafo: {error_msg}")
             return TripDataResponse(
                 final_report=None,
                 destination=final_response_state.get('destination'),
                 start_date=final_response_state.get('start_date'),
                 end_date=final_response_state.get('end_date'),
                 error=error_msg
             )

        print("Preparando resposta JSON...")
        response_data = TripDataResponse(
            final_report=final_response_state.get('final_report'), 
            destination=final_response_state.get('destination'),
            start_date=final_response_state.get('start_date'),
            end_date=final_response_state.get('end_date'),
            error=final_response_state.get('error') 
        )
        end_time = time.time()
        print(f"Respondendo com sucesso. Tempo total: {end_time - start_time:.2f} segundos.")
        return response_data

    except Exception as e:
        print(f"!!! Erro EXCEPCIONAL na API /plan-trip: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
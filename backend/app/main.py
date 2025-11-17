from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
# Importar os novos modelos Pydantic do langgraph_app
from app.langgraph_app import app, TravelAppState, FinalReport, CuratedRecommendation
from typing import List, Dict, Any
import time

class TripRequest(BaseModel):
    user_request: str

# --- NOSSO NOVO MODELO DE RESPOSTA ---
# Reflete a estrutura que o frontend espera
class TripDataResponse(BaseModel):
    final_report: FinalReport | None = Field(None)
    destination: str | None = Field(None)
    start_date: str | None = Field(None)
    end_date: str | None = Field(None)
    error: str | None = Field(None)


api = FastAPI()

origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        final_response_state = app.invoke(initial_state)
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
            final_report=final_response_state.get('final_report'), # <-- Passa o objeto JSON curado
            destination=final_response_state.get('destination'),
            start_date=final_response_state.get('start_date'),
            end_date=final_response_state.get('end_date'),
            error=final_response_state.get('error') # Pode haver um erro de extração, mas com relatório parcial
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
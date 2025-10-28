from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.langgraph_app import app, TravelAppState
from typing import List, Dict, Any
import time

class TripRequest(BaseModel):
    user_request: str

class TripDataResponse(BaseModel):
    flights: List[Dict[str, Any]] | None = Field(None)
    hotels: List[Dict[str, Any]] | None = Field(None)
    activities: List[Dict[str, Any]] | None = Field(None)
    itinerary: str = Field(...)
    destination: str | None = Field(None)
    start_date: str | None = Field(None)
    end_date: str | None = Field(None)
    error: str | None = Field(None)


api = FastAPI()

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/plan-trip", response_model=TripDataResponse)
async def plan_trip(request: TripRequest):
    print("--- Endpoint /plan-trip ACESSADO ---") # ADD 1
    start_time = time.time()
    print(f"Recebido user_request: {request.user_request}") # ADD 2
    initial_state = TravelAppState(
        user_request=request.user_request,
        destination=None,
        start_date=None,
        end_date=None,
        flights=None,
        hotels=None,
        activities=None,
        itinerary="",
        error=None
    )
    try:
        print("Invocando app.invoke...") # ADD 3
        final_response_state = app.invoke(initial_state)
        print("app.invoke concluído.") # ADD 4

        if final_response_state.get("error") and not final_response_state.get("flights") and not final_response_state.get("hotels") and not final_response_state.get("activities"):
             print(f"Erro retornado pelo grafo: {final_response_state['error']}") # ADD 5
             # Decide how to handle errors, maybe return it in the response instead of raising HTTPException for now
             # raise HTTPException(status_code=400, detail=final_response_state["error"])
             # Let's return the error in the response for debugging
             return TripDataResponse(
                 flights=final_response_state.get('flights', []),
                 hotels=final_response_state.get('hotels', []),
                 activities=final_response_state.get('activities', []),
                 itinerary=f"Erro no planejamento: {final_response_state['error']}",
                 destination=final_response_state.get('destination'),
                 start_date=final_response_state.get('start_date'),
                 end_date=final_response_state.get('end_date'),
                 error=final_response_state.get('error')
             )

        print("Preparando resposta JSON...") # ADD 6
        response_data = TripDataResponse(
            flights=final_response_state.get('flights'),
            hotels=final_response_state.get('hotels'),
            activities=final_response_state.get('activities'),
            itinerary=final_response_state.get('itinerary', "Itinerário não gerado."),
            destination=final_response_state.get('destination'),
            start_date=final_response_state.get('start_date'),
            end_date=final_response_state.get('end_date'),
            error=final_response_state.get('error')
        )
        end_time = time.time()
        print(f"Respondendo com sucesso. Tempo total: {end_time - start_time:.2f} segundos.") # ADD 7
        return response_data

    except Exception as e:
        print(f"!!! Erro EXCEPCIONAL na API /plan-trip: {e}") # ADD 8
        import traceback
        traceback.print_exc()
        # Retorna um erro 500 mais genérico se algo inesperado acontecer
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
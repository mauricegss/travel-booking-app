from typing import List, Dict, Optional
import os
import requests
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from functools import lru_cache
from tavily import TavilyClient

# --- Helper de Localização (só para voos) ---
@lru_cache(maxsize=100)
def _get_iata_code(city_name: str) -> str | None:
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("ERRO (Voos): TAVILY_API_KEY não configurada.")
        return None
    
    print(f"Tool (Voo-Helper): Buscando IATA para {city_name} usando Tavily...")
    query = f"Qual é o principal IATA code (código de aeroporto) para a cidade {city_name}? Responda APENAS o código de 3 letras (ex: 'GRU')."
    
    try:
        response = tavily_client.search(query=query, search_depth="basic", include_answer=True)
        answer = response.get('answer')
        
        if answer and len(answer) >= 3:
            iata = answer.strip().split(" ")[0][:3] # Pega os 3 primeiros caracteres
            print(f"Tavily (IATA) Answer: {iata}")
            return iata
        
        print(f"Tavily não retornou 'answer' para o IATA de {city_name}.")
        return None
    except Exception as e:
        print(f"Erro ao buscar IATA com Tavily: {e}")
        return None
# --- Fim do Helper ---

class FlightSearchInput(BaseModel):
    origin: str = Field(description="Cidade ou aeroporto de origem.")
    destination: str = Field(description="Cidade ou aeroporto de destino.")
    departure_date: str = Field(description="Data de partida no formato AAAA-MM-DD.")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato AAAA-MM-DD (opcional).")
    passengers: int = Field(default=1, description="Número de passageiros.")

@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, departure_date: str, **kwargs) -> List[Dict]:
    """Busca por horários de voos na API AviationStack com base na origem e destino."""
    print(f"Tool: Buscando voos REAIS (AviationStack) de {origin} para {destination}...")
    
    try:
        API_KEY = os.environ["AVIATIONSTACK_API_KEY"]
    except KeyError:
        return [{"id": "error", "airline": "AVIATIONSTACK_API_KEY não configurada.", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    origin_iata = _get_iata_code(origin)
    dest_iata = _get_iata_code(destination)
    
    if not origin_iata:
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para a origem: {origin}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
    if not dest_iata:
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para o destino: {destination}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    API_URL = "http://api.aviationstack.com/v1/flights" # HTTP no plano gratuito
    
    params = {
        "access_key": API_KEY,
        "dep_iata": origin_iata,
        "arr_iata": dest_iata,
        "flight_status": "scheduled", # Busca voos agendados
        "limit": 5
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        
        formatted_results = []
        if not data:
            return []

        for flight in data:
            airline_name = flight.get('airline', {}).get('name', 'N/A')
            flight_number = flight.get('flight', {}).get('number', '')
            
            # Gera um link de fallback para o Google Flights
            fallback_url = f"https://www.google.com/flights?q=Voo+{origin_iata}+para+{dest_iata}"
            
            formatted_results.append({
                "id": fallback_url,
                "airline": airline_name,
                "departure": "N/A",
                "arrival": "N/A",
                "duration": f"Voo {airline_name} {flight_number}", # O plano grátis não dá duração
                "price": "Verificar Preço", # O plano grátis não dá preço
                "stops": 0 # O plano grátis foca em voos individuais
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo da AviationStack.")
        return formatted_results

    except requests.exceptions.HTTPError as e:
        print(f"Erro na API AviationStack (Voos): {e.response.text}")
        return [{"id": "error", "airline": f"Erro na API de voos: {e.response.text}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
    except Exception as e:
        print(f"Erro inesperado (Voos): {e}")
        return [{"id": "error", "airline": f"Erro ao buscar voos: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
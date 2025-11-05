from typing import List, Dict, Optional
import os
import requests
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from functools import lru_cache
from tavily import TavilyClient

# --- Helper de Localização (JSON) ---
@lru_cache(maxsize=100)
def _get_iata_code(city_name: str) -> str | None:
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("ERRO (Voos): TAVILY_API_KEY não configurada.")
        return None
    
    print(f"Tool (Voo-Helper): Buscando IATA para {city_name} usando Tavily...")
    query = f"""
    Qual é o principal IATA code (código de aeroporto) para a cidade {city_name}?
    Responda APENAS com um objeto JSON no formato: {{"iataCode": "XXX"}}
    """
    
    try:
        response = tavily_client.search(query=query, search_depth="basic", include_answer=True)
        answer = response.get('answer')
        
        if answer:
            print(f"Tavily (IATA) Answer: {answer}")
            json_str = answer.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)

            if data.get('iataCode'):
                iata = data['iataCode']
                print(f"IATA Code extraído: {iata}")
                return iata
        
        print(f"Tavily não retornou 'answer' ou JSON válido para o IATA de {city_name}.")
        return None
    except Exception as e:
        print(f"Erro ao buscar/processar IATA com Tavily: {e}")
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

    API_URL = "http://api.aviationstack.com/v1/flights"
    
    params = {
        "access_key": API_KEY,
        "dep_iata": origin_iata,
        "arr_iata": dest_iata,
        "flight_status": "scheduled",
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
            
            # --- INÍCIO DA MELHORIA ---
            # 1. Cria um link de busca de preço muito melhor
            #    (O frontend espera um ID que seja um link clicável)
            google_flights_url = f"https://www.google.com/flights?q=Voo+de+{origin.replace(' ', '+')}+para+{destination.replace(' ', '+')}+em+{departure_date}"
            
            # 2. Informa o utilizador sobre o plano gratuito
            price_text = "Preço N/A (Plano Grátis)"
            
            # 3. Dá uma 'duração' mais informativa
            duration_text = f"Rota: {origin_iata} ➔ {dest_iata} (Voo {flight_number})"
            # --- FIM DA MELHORIA ---

            formatted_results.append({
                "id": google_flights_url, # <-- Melhoria 1
                "airline": airline_name,
                "departure": "N/A",
                "arrival": "N/A",
                "duration": duration_text, # <-- Melhoria 3
                "price": price_text, # <-- Melhoria 2
                "stops": 0
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo da AviationStack.")
        return formatted_results

    except requests.exceptions.HTTPError as e:
        print(f"Erro na API AviationStack (Voos): {e.response.text}")
        return [{"id": "error", "airline": f"Erro na API de voos: {e.response.text}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
    except Exception as e:
        print(f"Erro inesperado (Voos): {e}")
        return [{"id": "error", "airline": f"Erro ao buscar voos: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
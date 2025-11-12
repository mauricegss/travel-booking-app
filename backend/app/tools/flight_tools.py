from typing import List, Dict, Optional
import os
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from serpapi import GoogleSearch
from tavily import TavilyClient
from functools import lru_cache

# --- O Helper de IATA (Tavily) ---
@lru_cache(maxsize=100)
def _get_iata_code(city_name: str) -> str | None:
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("ERRO (Voo-Helper): TAVILY_API_KEY não configurada.")
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
    """Busca por voos usando a API Google Flights da SerpAPI."""
    print(f"Tool: Buscando voos REAIS (SerpAPI Google Flights) de {origin} para {destination}...")
    
    return_date = kwargs.get('return_date')
    passengers = kwargs.get('passengers', 1)

    try:
        SERPAPI_KEY = os.environ["SERPAPI_API_KEY"]
        if "TAVILY_API_KEY" not in os.environ:
            raise KeyError("TAVILY_API_KEY não configurada no .env")
            
    except KeyError as e:
        error_msg = f"{e.args[0]} não configurada."
        return [{"id": "error", "airline": error_msg, "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    origin_iata = _get_iata_code(origin)
    dest_iata = _get_iata_code(destination)

    if not origin_iata:
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para a origem: {origin}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
    if not dest_iata:
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para o destino: {destination}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    params = {
        "engine": "google_flights",
        "api_key": SERPAPI_KEY,
        "departure_id": origin_iata,
        "arrival_id": dest_iata,
        "outbound_date": departure_date,
        "adults": passengers,
        "currency": "BRL",
        "hl": "pt-br",
        "gl": "br"
    }

    if return_date:
        params["return_date"] = return_date

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            error_msg = results["error"]
            print(f"!!! Erro da SerpAPI (Voos): {error_msg}")
            return [{"id": "error", "airline": f"Erro na API de voos: {error_msg}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

        formatted_results = []
        data_to_parse = results.get("best_flights", [])
        
        if not data_to_parse:
            data_to_parse = results.get("other_flights", [])

        if not data_to_parse:
            print("SerpAPI não retornou 'best_flights' ou 'other_flights', mas não reportou erro.")
            return []

        for flight in data_to_parse:
            legs = flight.get("flights", [])
            if not legs:
                continue # Pula este resultado de voo se não tiver trechos

            outbound_leg = legs[0]
            departure_time = outbound_leg.get("departure_airport", {}).get("time", "N/A")
            arrival_time = outbound_leg.get("arrival_airport", {}).get("time", "N/A")

            # --- [INÍCIO DA MUDANÇA] ---
            # Se for uma viagem de ida E VOLTA, formatamos os dados de forma diferente
            if return_date and len(legs) > 1:
                return_leg = legs[1]
                
                # Sobrescrevemos as variáveis para refletir a viagem completa
                departure_time = f"Ida: {departure_time}" # Ex: "Ida: 09:55"
                # Usamos a partida do voo de volta como "chegada" (horário de retorno)
                arrival_time = f"Volta: {return_leg.get('departure_airport', {}).get('time', 'N/A')}" # Ex: "Volta: 18:00"
            # --- [FIM DA MUDANÇA] ---

            formatted_results.append({
                "id": flight.get("google_flights_url", "default_id"),
                "airline": flight.get("airline_logo_text", outbound_leg.get("airline", "N/A")),
                "departure": departure_time, # <-- Agora contém "Ida: ..."
                "arrival": arrival_time,     # <-- Agora contém "Volta: ..."
                "duration": flight.get("total_duration", "N/A"), # Duração total (ida+volta)
                "price": f"R$ {flight.get('price', 0)}", 
                "stops": flight.get("stops", 0)
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo da SerpAPI.")
        return formatted_results[:10]

    except Exception as e:
        print(f"Erro inesperado (Voos - SerpAPI): {e}")
        return [{"id": "error", "airline": f"Erro ao buscar voos na SerpAPI: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
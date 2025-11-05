from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from amadeus import ResponseError
from .amadeus_client import amadeus, get_location_data # <-- Importa nosso cliente

class FlightSearchInput(BaseModel):
    origin: str = Field(description="Cidade ou aeroporto de origem.")
    destination: str = Field(description="Cidade ou aeroporto de destino.")
    departure_date: str = Field(description="Data de partida no formato AAAA-MM-DD.")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato AAAA-MM-DD (opcional).")
    passengers: int = Field(default=1, description="Número de passageiros.")

@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, passengers: int = 1) -> List[Dict]:
    """Busca por opções de voos na API Amadeus com base na origem, destino, datas e número de passageiros."""
    print(f"Tool: Buscando voos REAIS (Amadeus) de {origin} para {destination}...")

    if not amadeus:
        return [{"id": "error", "airline": "Cliente Amadeus não inicializado. Verifique as API keys.", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    origin_data = get_location_data(origin)
    dest_data = get_location_data(destination)

    if not origin_data or not origin_data.get('iataCode'):
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para a origem: {origin}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
    if not dest_data or not dest_data.get('iataCode'):
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para o destino: {destination}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    origin_code = origin_data['iataCode']
    dest_code = dest_data['iataCode']

    try:
        search_params = {
            'originLocationCode': origin_code,
            'destinationLocationCode': dest_code,
            'departureDate': departure_date,
            'adults': passengers,
            'nonStop': 'false',
            'max': 5, # Pede os 5 primeiros resultados
            'currencyCode': 'BRL' # Pede preços em Reais Brasileiros
        }
        if return_date:
            search_params['returnDate'] = return_date

        response = amadeus.shopping.flight_offers_search.get(**search_params)
        
        dictionaries = response.result.get('dictionaries', {})
        carriers = dictionaries.get('carriers', {})

        formatted_results = []
        for offer in response.data:
            # Pega o nome da companhia aérea do dicionário
            airline_code = offer['itineraries'][0]['segments'][0]['carrierCode']
            airline_name = carriers.get(airline_code, airline_code)
            
            # Pega a duração (ex: 'PT5H30M' -> 5H 30M)
            duration_raw = offer['itineraries'][0]['duration'][2:].replace('H', 'H ').replace('M', 'M')
            
            # O frontend espera um link. Como a API não dá um, criamos um link de busca
            fallback_url = f"https://www.google.com/flights?q=Voo+{origin_code}+para+{dest_code}+em+{departure_date}"
            
            formatted_results.append({
                "id": fallback_url,
                "airline": airline_name,
                "departure": "N/A", # API Amadeus é complexa para horários, mantemos simples
                "arrival": "N/A",
                "duration": duration_raw,
                "price": f"R$ {offer['price']['total']}",
                "stops": len(offer['itineraries'][0]['segments']) - 1
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo da Amadeus.")
        return formatted_results

    except ResponseError as e:
        print(f"Erro na API Amadeus (Voos): {e.description}")
        return [{"id": "error", "airline": f"Erro na API de voos: {e.description}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
    except Exception as e:
        print(f"Erro inesperado (Voos): {e}")
        return [{"id": "error", "airline": f"Erro ao buscar voos: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
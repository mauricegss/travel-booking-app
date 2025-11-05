from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from amadeus import ResponseError
from .amadeus_client import amadeus, get_location_data

class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")
    adults: int = Field(default=1, description="Número de adultos.")
    rooms: int = Field(default=1, description="Número de quartos.")

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> List[Dict]:
    """Busca por opções de hotéis na API Amadeus com base no destino, datas, número de adultos e quartos."""
    print(f"Tool: Buscando hotéis REAIS (Amadeus) em {destination} de {check_in_date} até {check_out_date}...")

    if not amadeus:
        return [{"id": "error", "name": "Cliente Amadeus não inicializado. Verifique as API keys.", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    dest_data = get_location_data(destination)
    if not dest_data or not dest_data.get('iataCode'):
         return [{"id": "error", "name": f"Não foi possível encontrar o código IATA para o destino: {destination}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
    
    city_code = dest_data['iataCode']

    try:
        # --- INÍCIO DA CORREÇÃO ---
        # O nome correto do método é 'hotel_offers_search'
        response = amadeus.shopping.hotel_offers_search.get(
        # --- FIM DA CORREÇÃO ---
            cityCode=city_code,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults,
            roomQuantity=rooms,
            ratings='2,3,4,5',
            bestRateOnly=True,
            view='LIGHT',
            lang='PT'
        )
        
        # Limita a 5 resultados para não sobrecarregar a interface
        offers_to_process = response.data[:5]
        
        formatted_results = []
        for offer in offers_to_process:
            hotel = offer['hotel']
            hotel_offer = offer['offers'][0]
            
            price = f"{hotel_offer['price']['currency']} {hotel_offer['price']['total']}"
            
            description = "Descrição não disponível."
            if hotel.get('description') and hotel['description'].get('text'):
                description = hotel['description']['text']
            
            hotel_name_query = hotel['name'].replace(' ', '+')
            fallback_url = f"https://www.google.com/search?q=hotel+{hotel_name_query}+{destination}"
            
            formatted_results.append({
                "id": fallback_url,
                "name": hotel['name'],
                "location": hotel.get('address', {}).get('lines', ['Endereço não informado'])[0],
                "rating": int(hotel.get('rating', 0)),
                "price": price,
                "amenities": [description]
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel da Amadeus.")
        return formatted_results

    except ResponseError as e:
        print(f"Erro na API Amadeus (Hotéis): {e.description}")
        return [{"id": "error", "name": f"Erro na API de hotéis: {e.description}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
    except Exception as e:
        print(f"Erro inesperado (Hotéis): {e}")
        return [{"id": "error", "name": f"Erro ao buscar hotéis: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
from typing import List, Dict, Optional
import os
import requests
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from functools import lru_cache # <-- Importa o lru_cache
from tavily import TavilyClient

# --- Helper de Localização (para hotéis - Geoapify) ---
@lru_cache(maxsize=100)
def _get_geocode(city_name: str) -> Dict | None:
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("ERRO (Hotéis): TAVILY_API_KEY não configurada.")
        return None
    
    print(f"Tool (Hotel-Helper): Buscando Coordenadas para {city_name} usando Tavily...")
    # Este prompt para GeoCode funcionou bem no seu log anterior
    query = f"Quais são a latitude e longitude de {city_name}? Responda APENAS com um objeto JSON no formato: {{\"latitude\": 0.0, \"longitude\": 0.0}}"
    
    try:
        response = tavily_client.search(query=query, search_depth="basic", include_answer=True)
        answer = response.get('answer')
        
        if answer:
            print(f"Tavily (GeoCode) Answer: {answer}")
            json_str = answer.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)
            if data.get('latitude') and data.get('longitude'):
                return data
        
        print(f"Tavily não retornou 'answer' para GeoCode de {city_name}.")
        return None
    except Exception as e:
        print(f"Erro ao buscar GeoCode com Tavily: {e}")
        return None
# --- Fim do Helper ---

class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")
    adults: int = Field(default=1, description="Número de adultos.")
    rooms: int = Field(default=1, description="Número de quartos.")

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, **kwargs) -> List[Dict]:
    """Busca por opções de hotéis na API Geoapify com base nas coordenadas do destino."""
    print(f"Tool: Buscando hotéis REAIS (Geoapify) em {destination}...")
    
    try:
        API_KEY = os.environ["GEOAPIFY_API_KEY"]
    except KeyError:
        return [{"id": "error", "name": "GEOAPIFY_API_KEY não configurada.", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    geo_code = _get_geocode(destination)
    if not geo_code:
        return [{"id": "error", "name": f"Não foi possível encontrar coordenadas para {destination}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    API_URL = "https://api.geoapify.com/v2/places"
    
    params = {
        "categories": "accommodation.hotel,accommodation.guest_house",
        "filter": f"circle:{geo_code['longitude']},{geo_code['latitude']},5000", # Raio de 5km
        "bias": f"proximity:{geo_code['longitude']},{geo_code['latitude']}",
        "limit": 5,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json().get("features", [])
        
        formatted_results = []
        if not data:
            return []

        for feature in data:
            props = feature.get("properties", {})
            
            hotel_name = props.get("name", "Hotel sem nome")
            address = props.get("address_line2", "Endereço não informado")
            
            # Gera um link de fallback do Google Maps
            fallback_url = f"https://www.google.com/maps?q={hotel_name.replace(' ', '+')}+{address.replace(' ', '+')}"
            
            formatted_results.append({
                "id": fallback_url,
                "name": hotel_name,
                "location": address,
                "rating": 0, # Geoapify não fornece rating de estrelas
                "price": "Verificar Preço",
                "amenities": [props.get("datasource", {}).get("raw", {}).get("phone", "Contacto não disponível")]
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel da Geoapify.")
        return formatted_results

    except requests.exceptions.HTTPError as e:
        print(f"Erro na API Geoapify (Hotéis): {e.response.text}")
        return [{"id": "error", "name": f"Erro na API de hotéis: {e.response.text}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
    except Exception as e:
        print(f"Erro inesperado (Hotéis): {e}")
        return [{"id": "error", "name": f"Erro ao buscar hotéis: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
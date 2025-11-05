from typing import List, Dict, Optional
import os
import requests
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Esquema de Input para Hotéis ---
class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade de destino para a busca de hotéis.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")

# Helper para obter coordenadas da cidade usando Geoapify
def _get_city_coordinates(city_name: str, api_key: str) -> Optional[Dict[str, float]]:
    print(f"Tool (Hotel-Helper): Buscando coordenadas para {city_name} (Geoapify Geocoding)")
    GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": city_name,
        "apiKey": api_key,
        "limit": 1
    }
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            # Geoapify retorna [lon, lat]
            return {"lon": coords[0], "lat": coords[1]}
        return None
    except Exception as e:
        print(f"Erro ao buscar coordenadas no Geoapify: {e}")
        return None

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> List[Dict]:
    """Busca por hotéis na API Geoapify com base no destino e datas."""
    print(f"Tool: Buscando hotéis REAIS (Geoapify) em {destination}...")
    
    try:
        API_KEY = os.environ["GEOAPIFY_API_KEY"]
    except KeyError:
        print("ERRO (Hotéis): GEOAPIFY_API_KEY não configurada.")
        return [{"id": "error", "name": "GEOAPIFY_API_KEY não configurada.", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    # 1. Obter coordenadas da cidade
    coords = _get_city_coordinates(destination, API_KEY)
    if not coords:
        return [{"id": "error", "name": f"Não foi possível encontrar coordenadas para {destination}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    # 2. Buscar locais (hotéis) perto dessas coordenadas
    PLACES_URL = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "accommodation.hotel",
        # --- MUDANÇA 1: Aumentamos o raio para 10km ---
        "filter": f"circle:{coords['lon']},{coords['lat']},10000", # Raio de 10km
        "bias": f"proximity:{coords['lon']},{coords['lat']}",
        # --- MUDANÇA 2: Aumentamos o limite para 10 ---
        "limit": 10, # Damos 10 opções para a IA filtrar
        "apiKey": API_KEY
    }
    
    try:
        response = requests.get(PLACES_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('features', [])
        formatted_results = []
        if not results:
            print("Geoapify não retornou resultados para hotéis.")
            return []

        # Mapeia os resultados do Geoapify para o formato ApiHotel
        for res in results:
            props = res.get('properties', {})
            # Monta um link de busca do Google
            google_search_url = f"https://www.google.com/search?q={props.get('name', 'hotel').replace(' ', '+')}+{destination.replace(' ', '+')}"
            
            formatted_results.append({
                "id": props.get('datasource', {}).get('raw', {}).get('osm_id', google_search_url), # Usa o URL do Google como ID/link
                "name": props.get('name', 'Hotel não identificado'),
                "location": props.get('address_line2', destination), # Endereço ou cidade
                "rating": 0, # Geoapify (plano gratuito) não fornece rating
                "price": "Verificar no site",
                "amenities": [props.get('address_line1', 'Endereço não disponível')] # Usamos amenities para a descrição
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel da Geoapify.")
        return formatted_results

    except Exception as e:
        print(f"Erro inesperado (Hotéis - Geoapify): {e}")
        return [{"id": "error", "name": f"Erro ao buscar hotéis: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
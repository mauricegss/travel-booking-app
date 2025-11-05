from typing import List, Dict, Optional
import os
import requests
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Helper de Coordenadas (Copiado do hotel_tools) ---
def _get_city_coordinates(city_name: str, api_key: str) -> Optional[Dict[str, float]]:
    print(f"Tool (Activity-Helper): Buscando coordenadas para {city_name} (Geoapify Geocoding)")
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
# --- Fim do Helper ---

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início (usada para contexto, não para filtro de API).")
    end_date: str = Field(description="Data de fim (usada para contexto, não para filtro de API).")

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, **kwargs) -> List[Dict]:
    """Busca por atrações turísticas na API Geoapify com base no destino."""
    print(f"Tool: Buscando atividades REAIS (Geoapify) em {destination}...")
    
    try:
        API_KEY = os.environ["GEOAPIFY_API_KEY"]
    except KeyError:
        print("ERRO (Atividades): GEOAPIFY_API_KEY não configurada.")
        return [{"id": "error", "title": "GEOAPIFY_API_KEY não configurada", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]

    # 1. Obter coordenadas da cidade
    coords = _get_city_coordinates(destination, API_KEY)
    if not coords:
        return [{"id": "error", "title": f"Não foi possível encontrar coordenadas para {destination}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]

    # 2. Buscar locais (atrações) perto dessas coordenadas
    PLACES_URL = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "tourism.attraction,leisure.park,entertainment.museum,entertainment.zoo,commercial.shopping_mall,catering.restaurant",
        "filter": f"circle:{coords['lon']},{coords['lat']},15000", # Raio de 15km
        "limit": 50, # Aumentado para 50 para dar mais opções ao Agente Curador
        "apiKey": API_KEY
    }
    
    try:
        response = requests.get(PLACES_URL, params=params)
        response.raise_for_status() # Isso vai disparar o erro se a URL falhar
        
        data = response.json()
        
        results = data.get('features', [])
        formatted_results = []
        if not results:
            print("Geoapify não retornou resultados para atividades.")
            return []

        # Mapeia os resultados do Geoapify para o formato ApiActivity
        for res in results:
            props = res.get('properties', {})
            
            # Monta um link de busca do Google
            google_search_url = f"https://www.google.com/search?q={props.get('name', 'atividade').replace(' ', '+')}+{destination.replace(' ', '+')}"
            
            # Tenta pegar uma descrição, se não houver, usa o endereço
            description = props.get('address_line2', 'Atração local')
            
            # Pega a categoria principal para usar como "Fonte"
            category = props.get('categories', ['tourism'])[0].split('.')[0] # ex: "tourism" ou "leisure"

            formatted_results.append({
                "id": google_search_url, # Usa o URL do Google como ID/link
                "title": props.get('name', 'Atração não identificada'),
                "description": description,
                "duration": "N/A", # Atrações não têm duração fixa
                "price": "Verificar no site",
                "capacity": category.capitalize() # Fonte (ex: "Tourism", "Leisure")
            })
        
        print(f"Retornando {len(formatted_results)} opções de atividade da Geoapify.")
        return formatted_results

    except requests.exceptions.HTTPError as e:
        # Erro HTTP (como o 400 Bad Request)
        print(f"!!! Erro na API Geoapify (Atividades): {e.response.text}")
        return [{"id": "error", "title": f"Erro na API de atividades: {e.response.text}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
    except Exception as e:
        # Outros erros (ex: timeout, parsing de JSON)
        print(f"!!! Erro inesperado (Atividades - Geoapify): {e}")
        return [{"id": "error", "title": f"Erro ao buscar atividades: {e}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
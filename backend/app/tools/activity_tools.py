from typing import List, Dict
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from amadeus import ResponseError
from .amadeus_client import amadeus, get_location_data

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início das atividades no formato AAAA-MM-DD.")
    end_date: str = Field(description="Data de fim das atividades no formato AAAA-MM-DD.")

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, start_date: str, end_date: str) -> List[Dict]:
    """Busca por atividades e atrações na API Amadeus no destino para o período especificado."""
    print(f"Tool: Buscando atividades REAIS (Amadeus) em {destination}...")
    
    if not amadeus:
        return [{"id": "error", "title": "Cliente Amadeus não inicializado. Verifique as API keys.", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]

    dest_data = get_location_data(destination)
    if not dest_data or not dest_data.get('geoCode'):
         return [{"id": "error", "title": f"Não foi possível encontrar coordenadas para: {destination}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
    
    geo_code = dest_data['geoCode']

    try:
        response = amadeus.shopping.activities.get(
            latitude=geo_code['latitude'],
            longitude=geo_code['longitude'],
            radius=20
        )
        
        # --- INÍCIO DA CORREÇÃO ---
        # 1. Limita a 5 resultados
        activities_to_process = response.data[:5]
        # --- FIM DA CORREÇÃO ---
        
        formatted_results = []
        for activity in activities_to_process:
            price = "Verificar no site"
            if activity.get('price'):
                price = f"{activity['price']['currencyCode']} {activity['price']['amount']}"
            
            booking_link = activity.get('links', {}).get('booking', 'N/A')
            
            if booking_link == 'N/A':
                 booking_link = f"https://www.google.com/search?q={activity['name'].replace(' ', '+')}"
            
            # --- INÍCIO DA CORREÇÃO ---
            # 2. Usa o campo 'rating' em vez de 'capacity' (Provedor Online)
            capacity_text = f"Avaliação: {activity.get('rating', 'N/A')}"
            # --- FIM DA CORREÇÃO ---
            
            formatted_results.append({
                "id": booking_link,
                "title": activity['name'],
                "description": activity.get('shortDescription', 'Sem descrição...'),
                "duration": "N/A",
                "price": price,
                "capacity": capacity_text # <-- Usa o texto de avaliação
            })
        
        print(f"Retornando {len(formatted_results)} opções de atividade da Amadeus.")
        return formatted_results

    except ResponseError as e:
        print(f"Erro na API Amadeus (Atividades): {e.description}")
        return [{"id": "error", "title": f"Erro na API de atividades: {e.description}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
    except Exception as e:
        print(f"Erro inesperado (Atividades): {e}")
        return [{"id": "error", "title": f"Erro ao buscar atividades: {e}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
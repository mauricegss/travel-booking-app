from typing import List, Dict
import os
import requests
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from unidecode import unidecode # <-- A IMPORTAÇÃO NECESSÁRIA

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início das atividades no formato AAAA-MM-DD.")
    end_date: str = Field(description="Data de fim das atividades no formato AAAA-MM-DD.")

# Helper para formatar data (Ticketmaster exige formato ISO 8601)
def format_datetime_iso(date_str: str) -> str:
    return f"{date_str}T00:00:00Z"

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, start_date: str, end_date: str) -> List[Dict]:
    """Busca por atividades e eventos na API Ticketmaster com base no destino e datas."""
    print(f"Tool: Buscando atividades REAIS (Ticketmaster) em {destination}...")
    
    try:
        TICKETMASTER_API_KEY = os.environ["TICKETMASTER_API_KEY"]
    except KeyError:
        return [{"id": "error", "title": "TICKETMASTER_API_KEY não configurada no .env", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]

    API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    # Limpa o nome da cidade (ex: "São Paulo" -> "Sao Paulo")
    city_normalized = unidecode(destination)
    
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city_normalized,
        "startDateTime": format_datetime_iso(start_date),
        "endDateTime": format_datetime_iso(end_date),
        "size": 5, # Limita a 5 resultados
        "sort": "date,asc",
        "segmentName": "Music,Sports,Arts & Theater" # Foca em eventos
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        
        data = response.json().get("_embedded", {}).get("events", [])
        
        formatted_results = []
        if not data:
            return []

        for event in data:
            # Preço (pode não existir)
            price_range = event.get("priceRanges", [])
            price = "Verificar no site"
            if price_range:
                price = f"A partir de {price_range[0].get('min', '?')} {price_range[0].get('currency', '')}"
            
            # Descrição (pode não existir)
            description = event.get('info', event.get('description', 'Sem descrição...'))
            
            # Local (Venue)
            venue = "Local não informado"
            if event.get("_embedded", {}).get("venues", []):
                venue = event["_embedded"]["venues"][0].get("name", venue)

            formatted_results.append({
                "id": event.get('url', '#'), # Link real do Ticketmaster
                "title": event['name'],
                "description": description,
                "duration": "N/A (Evento)",
                "price": price,
                "capacity": f"Local: {venue}" # O frontend usa 'capacity' como "Fonte:"
            })
        
        print(f"Retornando {len(formatted_results)} opções de atividade da Ticketmaster.")
        return formatted_results

    except requests.exceptions.HTTPError as e:
        print(f"Erro na API Ticketmaster: {e.response.text}")
        return [{"id": "error", "title": f"Erro na API de atividades: {e.response.text}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
    except Exception as e:
        print(f"Erro inesperado (Atividades): {e}")
        return [{"id": "error", "title": f"Erro ao buscar atividades: {e}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
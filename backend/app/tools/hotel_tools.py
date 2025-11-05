from typing import List, Dict, Optional
import os
import requests
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from datetime import datetime
from tavily import TavilyClient # Importa Tavily
from functools import lru_cache # <-- ESTA ERA A LINHA EM FALTA

# --- Helper para buscar o ID da cidade no Kiwi (usando Tavily) ---
@lru_cache(maxsize=100)
def get_kiwi_city_id(city_name: str) -> str | None:
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("ERRO: TAVILY_API_KEY não configurada no .env")
        return None
    
    print(f"Tool (Helper): Buscando Kiwi 'city_id' para {city_name} usando Tavily...")
    
    # Pergunta à IA da Tavily o ID específico do Kiwi
    query = f"Qual é o ID da cidade (city_id) para '{city_name}' na API Tequila Kiwi.com? Responda APENAS o ID (ex: 'city:CWB')."
    
    try:
        response = tavily_client.search(
            query=query, 
            search_depth="basic", 
            include_answer=True
        )
        answer = response.get('answer')
        
        if answer:
            print(f"Tavily (Kiwi ID) Answer: {answer}")
            return answer.strip() # Retorna o ID (ex: "city:CWB")
        
        print(f"Tavily não retornou 'answer' para o ID de {city_name}.")
        return None
        
    except Exception as e:
        print(f"Erro ao buscar ID do Kiwi com Tavily: {e}")
        return None
# --- Fim do Helper ---


class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")
    adults: int = Field(default=1, description="Número de adultos.")
    rooms: int = Field(default=1, description="Número de quartos.")

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> List[Dict]:
    """Busca por opções de hotéis na API Kiwi.com (Tequila) após encontrar o ID da cidade com o Tavily."""
    print(f"Tool: Buscando hotéis REAIS (Kiwi.com) em {destination}...")

    # 1. Obter o 'city_id'
    city_id = get_kiwi_city_id(destination)
    if not city_id:
        return [{"id": "error", "name": f"Não foi possível encontrar o ID da localização para {destination} (Tavily/Kiwi)", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    try:
        KIWI_API_KEY = os.environ["KIWI_API_KEY"]
    except KeyError:
        return [{"id": "error", "name": "KIWI_API_KEY não configurada no .env", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    API_URL = "https://api.tequila.kiwi.com/v2/hotels"
    
    headers = {
        "apikey": KIWI_API_KEY
    }
    
    params = {
        "city_id": city_id,
        "check_in": check_in_date,
        "check_out": check_out_date,
        "adults_num": adults,
        "rooms_num": rooms,
        "curr": "BRL",
        "limit": 5
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json().get("data", {}).get("hotels", [])
        
        formatted_results = []
        if not data:
            return []

        for hotel in data:
            # A API de hotéis do Kiwi não dá um link de reserva,
            # então voltamos ao fallback do Google Search
            hotel_name_query = hotel['name'].replace(' ', '+')
            fallback_url = f"https{hotel_name_query}+{destination}"
            
            # A API de hotéis do Kiwi não retorna descrição,
            # usamos as 'amenities' que ela fornece
            amenities_list = hotel.get('amenities', [])
            description = ", ".join(amenities_list) if amenities_list else "Sem descrição ou comodidades."

            formatted_results.append({
                "id": fallback_url,
                "name": hotel['name'],
                "location": hotel.get('address', 'Endereço não informado'),
                "rating": int(hotel.get('stars', 0)),
                "price": f"R$ {hotel.get('price', 'N/A')}",
                "amenities": [description] # O frontend espera uma lista
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel da Kiwi.com.")
        return formatted_results

    except requests.exceptions.HTTPError as e:
        print(f"Erro na API Kiwi (Hotéis): {e.response.text}")
        return [{"id": "error", "name": f"Erro na API de hotéis: {e.response.text}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
    except Exception as e:
        print(f"Erro inesperado (Hotéis): {e}")
        return [{"id": "error", "name": f"Erro ao buscar hotéis: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
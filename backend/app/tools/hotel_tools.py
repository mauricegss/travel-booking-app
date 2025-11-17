from typing import List, Dict, Optional
import os
import requests
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from serpapi import GoogleSearch # <-- Importar GoogleSearch
import re # <-- Importar re para limpar o preço

# --- Esquema de Input para Hotéis (sem mudança) ---
class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade de destino para a busca de hotéis.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")

# --- REMOVEMOS O HELPER _get_city_coordinates (não é mais necessário) ---

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> List[Dict]:
    """Busca por hotéis usando a API Google Hotels da SerpAPI."""
    print(f"Tool: Buscando hotéis REAIS (SerpAPI Google Hotels) em {destination}...")
    
    try:
        # Usamos a mesma chave da API de Voos
        API_KEY = os.environ["SERPAPI_API_KEY"]
    except KeyError:
        print("ERRO (Hotéis): SERPAPI_API_KEY não configurada.")
        return [{"id": "error", "name": "SERPAPI_API_KEY não configurada.", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    # 1. Definir os parâmetros para a SerpAPI Google Hotels
    params = {
        "engine": "google_hotels",
        "api_key": API_KEY,
        "q": f"hotéis em {destination}",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "BRL",
        "hl": "pt-br",
        "gl": "br"
    }
    
    try:
        # 2. Executar a busca
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            error_msg = results["error"]
            print(f"!!! Erro da SerpAPI (Hotéis): {error_msg}")
            return [{"id": "error", "name": f"Erro na API de hotéis: {error_msg}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

        formatted_results = []
        # Os resultados principais geralmente estão em "properties"
        data_to_parse = results.get("properties", [])
        
        if not data_to_parse:
            print("SerpAPI (Hotéis) não retornou 'properties', mas não reportou erro.")
            return []

        # 3. Mapear os resultados para o formato ApiHotel
        for hotel in data_to_parse[:10]: # Limitamos a 10 opções para o agente curador
            
            # O link direto é a chave para sua segunda pergunta
            hotel_link = hotel.get("link", f"https://www.google.com/search?q={hotel.get('name', 'hotel').replace(' ', '+')}+{destination.replace(' ', '+')}")
            
            price_str = hotel.get("price", "Verificar no site")
            
            # Limpa o preço para ficar mais legível (ex: "R$ 500 total")
            if "total" in price_str:
                 price_str = price_str.split("total")[0].strip()

            # Usamos "highlights" (destaques) como amenidades
            amenities_list = hotel.get("highlights", []) 
            if not amenities_list and hotel.get("description"):
                 amenities_list = [hotel.get("description")]

            formatted_results.append({
                "id": hotel_link, # <-- O LINK ESTÁ AQUI
                "name": hotel.get("name", "Hotel não identificado"),
                "location": hotel.get("vicinity", hotel.get("address", destination)), # Bairro ou Endereço
                "rating": int(hotel.get("rating", 0) or 0), # Garantir que seja int
                "price": price_str,
                "amenities": amenities_list
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel da SerpAPI.")
        return formatted_results

    except Exception as e:
        print(f"Erro inesperado (Hotéis - SerpAPI): {e}")
        return [{"id": "error", "name": f"Erro ao buscar hotéis na SerpAPI: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
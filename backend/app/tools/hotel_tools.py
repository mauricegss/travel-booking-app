from typing import List, Dict, Optional
import os
import requests
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from serpapi import GoogleSearch
import re
from app.tools.image_tools import search_image # <-- IMPORTAR A NOVA FERRAMENTA

# --- Esquema de Input (sem mudança) ---
class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade de destino para a busca de hotéis.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> List[Dict]:
    """Busca por hotéis usando a API Google Hotels da SerpAPI e anexa uma imagem."""
    print(f"Tool: Buscando hotéis REAIS (SerpAPI Google Hotels) em {destination}...")
    
    try:
        API_KEY = os.environ["SERPAPI_API_KEY"]
    except KeyError:
        print("ERRO (Hotéis): SERPAPI_API_KEY não configurada.")
        return [{"id": "error", "name": "SERPAPI_API_KEY não configurada.", "location": "", "rating": 0, "price": "R$ 0", "amenities": [], "image_url": None}]

    params = {
        "engine": "google_hotels",
        "api_key": API_KEY,
        "q": f"hotéis em {destination}",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": 1, # <-- ATUALIZADO: Define busca para 1 pessoa
        "currency": "BRL",
        "hl": "pt-br",
        "gl": "br"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            error_msg = results["error"]
            print(f"!!! Erro da SerpAPI (Hotéis): {error_msg}")
            return [{"id": "error", "name": f"Erro na API de hotéis: {error_msg}", "location": "", "rating": 0, "price": "R$ 0", "amenities": [], "image_url": None}]

        formatted_results = []
        data_to_parse = results.get("properties", [])
        
        if not data_to_parse:
            print("SerpAPI (Hotéis) não retornou 'properties', mas não reportou erro.")
            return []

        # Limitamos a 5-7 para não fazer tantas chamadas de imagem
        for hotel in data_to_parse[:7]: 
            
            hotel_link = hotel.get("link", f"https://www.google.com/search?q={hotel.get('name', 'hotel').replace(' ', '+')}+{destination.replace(' ', '+')}")
            
            # --- LÓGICA DE PREÇO ATUALIZADA ---
            # Tenta pegar do campo estruturado rate_per_night -> lowest
            rate_info = hotel.get("rate_per_night", {})
            price_str = rate_info.get("lowest")
            
            # Se não achar, tenta pegar o preço total
            if not price_str:
                total_rate = hotel.get("total_rate", {})
                price_str = total_rate.get("lowest")

            # Fallback final para lógica antiga se ainda for None
            if not price_str:
                price_str = hotel.get("price", "Verificar no site")
                if "total" in price_str:
                     price_str = price_str.split("total")[0].strip()
            # ----------------------------------

            amenities_list = hotel.get("highlights", []) 
            if not amenities_list and hotel.get("description"):
                 amenities_list = [hotel.get("description")]

            hotel_name = hotel.get('name', 'Hotel não identificado')
            
            # --- NOVA ADIÇÃO: BUSCAR IMAGEM ---
            image_url = search_image.invoke({"query": f"{hotel_name} {destination}"})
            # ------------------------------------

            formatted_results.append({
                "id": hotel_link,
                "name": hotel_name,
                "location": hotel.get("vicinity", hotel.get("address", destination)),
                "rating": int(hotel.get("rating", 0) or 0),
                "price": price_str,
                "amenities": amenities_list,
                "image_url": image_url # <-- ANEXAR A IMAGEM
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel da SerpAPI (com imagens).")
        return formatted_results

    except Exception as e:
        print(f"Erro inesperado (Hotéis - SerpAPI): {e}")
        return [{"id": "error", "name": f"Erro ao buscar hotéis: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": [], "image_url": None}]
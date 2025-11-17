from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from serpapi import GoogleSearch
from functools import lru_cache

class ImageSearchInput(BaseModel):
    query: str = Field(description="O termo de busca para a imagem (ex: 'Qoya Hotel Curitiba', 'Museu Oscar Niemeyer').")

# Usamos um cache simples para não buscar a mesma imagem várias vezes na mesma execução
@lru_cache(maxsize=50)
def _search_google_images(query: str, api_key: str) -> List[str]:
    """Função auxiliar interna com cache para buscar imagens no SerpAPI."""
    print(f"Tool (Image-Helper): Buscando imagens (SerpAPI) para '{query}'...")
    
    params = {
        "engine": "google_images", # Você pode trocar para "google_images_light" se preferir
        "api_key": api_key,
        "q": query,
        "hl": "pt-br",
        "gl": "br",
        "tbm": "isch", # Indica que é uma busca de imagem
        "num": 5 # Pedimos 5, mas geralmente só usaremos a primeira
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"!!! Erro da SerpAPI (Imagens): {results['error']}")
            return []

        image_urls = []
        for image in results.get("images_results", []):
            # Priorizamos a imagem original, mas usamos a thumbnail como fallback
            if "original" in image:
                image_urls.append(image["original"])
            elif "thumbnail" in image:
                image_urls.append(image["thumbnail"])
        
        return image_urls

    except Exception as e:
        print(f"Erro inesperado (Imagens - SerpAPI): {e}")
        return []

@tool(args_schema=ImageSearchInput)
def search_image(query: str) -> str | None:
    """
    Busca UMA imagem relacionada a um termo de busca.
    Retorna a URL da primeira imagem encontrada ou None.
    """
    try:
        API_KEY = os.environ["SERPAPI_API_KEY"]
    except KeyError:
        print("ERRO (Imagens): SERPAPI_API_KEY não configurada.")
        return None
        
    urls = _search_google_images(query, API_KEY)
    
    if urls:
        print(f"Tool (Image): Encontrada imagem para '{query}': {urls[0]}")
        return urls[0]
    
    print(f"Tool (Image): Nenhuma imagem encontrada para '{query}'.")
    return None
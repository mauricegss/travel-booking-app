from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from serpapi import GoogleSearch
from app.tools.image_tools import search_image # <-- IMPORTAR A NOVA FERRAMENTA

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início (usada para contexto, não para filtro de API).")
    end_date: str = Field(description="Data de fim (usada para contexto, não para filtro de API).")

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, **kwargs) -> List[Dict]:
    """Busca por atrações turísticas na cidade de destino usando SerpAPI (Google Local)."""
    print(f"Tool: Buscando atividades REAIS (SerpAPI Google Local) em {destination}...")
    
    try:
        API_KEY = os.environ["SERPAPI_API_KEY"]
    except KeyError:
        print("ERRO (Atividades): SERPAPI_API_KEY não configurada.")
        return [{"id": "error", "title": "SERPAPI_API_KEY não configurada", "description": "", "duration": "", "price": "R$ 0", "capacity": "", "image_url": None}]

    params = {
        "engine": "google_local",
        "q": f"principais atraçoes turisticas em {destination}",
        "location": "Brazil",
        "gl": "br",
        "hl": "pt-br",
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"Erro na API SerpAPI: {results['error']}")
            return [{"id": "error", "title": f"Erro na API SerpAPI: {results['error']}", "description": "", "duration": "", "price": "R$ 0", "capacity": "", "image_url": None}]

        local_results = results.get('local_results', [])
        formatted_results = []
        
        if not local_results:
            print("SerpAPI google_local não retornou resultados.")
            return []

        # Pega as top 15 atrações
        for res in local_results[:15]:
            title = res.get('title', 'Atração não identificada')
            rating = res.get('rating')
            reviews = res.get('reviews')
            address = res.get('address', 'Endereço não disponível')
            type_str = res.get('type', 'Atração Turística')
            
            # Constrói uma descrição detalhada
            desc_parts = []
            if type_str:
                desc_parts.append(type_str)
            if rating:
                desc_parts.append(f"Avaliação: {rating}⭐ ({reviews} avaliações)")
            if address:
                desc_parts.append(f"Local: {address}")
                
            description = " | ".join(desc_parts)

            # Buscar imagem de vitrine
            image_url = search_image.invoke({"query": f"{title} {destination} tourism"})

            formatted_results.append({
                "id": res.get('place_id') or f"https://www.google.com/search?q={title.replace(' ', '+')}+{destination.replace(' ', '+')}", 
                "title": title,
                "description": description,
                "duration": "N/A",
                "price": "Verificar no local",
                "capacity": "Atração sugerida",
                "image_url": image_url
            })
        
        print(f"Retornando {len(formatted_results)} opções de atividade via Google Local.")
        return formatted_results

    except Exception as e:
        print(f"!!! Erro inesperado (Atividades - SerpAPI): {e}")
        return [{"id": "error", "title": f"Erro ao buscar atividades: {e}", "description": "", "duration": "", "price": "R$ 0", "capacity": "", "image_url": None}]
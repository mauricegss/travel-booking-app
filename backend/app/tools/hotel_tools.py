from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient
from urllib.parse import urlparse # <-- ADICIONE IMPORT

class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")
    adults: int = Field(default=1, description="Número de adultos.")
    rooms: int = Field(default=1, description="Número de quartos.")

# --- NOVA FUNÇÃO HELPER ---
def _get_domain(url: str) -> str:
    if not url:
        return "Fonte desconhecida"
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return "Fonte desconhecida"
# --- FIM DA NOVA FUNÇÃO ---

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> List[Dict]:
    """Busca por opções de hotéis na web com base no destino, datas, número de adultos e quartos."""
    print(f"Tool: Buscando hotéis REAIS em {destination} de {check_in_date} até {check_out_date}...")

    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        return [{"id": "error", "name": "API Key de Busca (Tavily) não configurada", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    query = f"Opções de hotéis em {destination} para {adults} adultos, de {check_in_date} até {check_out_date}"

    try:
        search_response = tavily_client.search(query=query, search_depth="basic", include_answer=False, max_results=5)
        web_results = search_response.get("results", [])
        
        formatted_results = []
        if not web_results:
             return []

        for result in web_results:
            url = result.get("url")
            formatted_results.append({
                "id": url,
                "name": result.get("title", "Título não disponível"),
                "location": _get_domain(url), # <-- MUDANÇA AQUI
                "rating": 0,
                "price": "Verificar no site",
                "amenities": [result.get("content", "Sem descrição...")]
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel encontradas na web.")
        return formatted_results

    except Exception as e:
        return [{"id": "error", "name": f"Erro na busca: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
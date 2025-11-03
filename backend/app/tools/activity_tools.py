from typing import List, Dict
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient
from urllib.parse import urlparse # <-- ADICIONE IMPORT

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início das atividades no formato AAAA-MM-DD.")
    end_date: str = Field(description="Data de fim das atividades no formato AAAA-MM-DD.")

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

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, start_date: str, end_date: str) -> List[Dict]:
    """Busca por atividades e atrações na web no destino para o período especificado."""
    print(f"Tool: Buscando atividades REAIS em {destination} entre {start_date} e {end_date}.")

    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        return [{"id": "error", "title": "API Key de Busca (Tavily) não configurada", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]

    query = f"atividades, passeios ou 'o que fazer' em {destination} para as datas {start_date} até {end_date}"

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
                "title": result.get("title", "Título não disponível"),
                "description": result.get("content", "Sem descrição..."),
                "duration": "N/A",
                "price": "Verificar no site",
                "capacity": _get_domain(url) # <-- MUDANÇA AQUI
            })
        
        print(f"Retornando {len(formatted_results)} opções de atividade encontradas na web.")
        return formatted_results

    except Exception as e:
        return [{"id": "error", "title": f"Erro na busca: {e}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
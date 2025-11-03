from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient 
from urllib.parse import urlparse # <-- ADICIONE IMPORT

class FlightSearchInput(BaseModel):
    origin: str = Field(description="Cidade ou aeroporto de origem.")
    destination: str = Field(description="Cidade ou aeroporto de destino.")
    departure_date: str = Field(description="Data de partida no formato AAAA-MM-DD.")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato AAAA-MM-DD (opcional).")
    passengers: int = Field(default=1, description="Número de passageiros.")

# --- NOVA FUNÇÃO HELPER ---
def _get_domain(url: str) -> str:
    if not url:
        return "Fonte desconhecida"
    try:
        domain = urlparse(url).netloc
        # Remove "www." se existir
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return "Fonte desconhecida"
# --- FIM DA NOVA FUNÇÃO ---

@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, passengers: int = 1) -> List[Dict]:
    """Busca por opções de voos na web com base na origem, destino, datas e número de passageiros."""
    print(f"Tool: Buscando voos REAIS de {origin} para {destination} de {departure_date} {('até ' + return_date) if return_date else ''}...")

    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        return [{"id": "error", "airline": "API Key de Busca (Tavily) não configurada", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    query = f"voos de {origin} para {destination} partindo em {departure_date} e retornando em {return_date} para {passengers} passageiro(s)"

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
                "airline": _get_domain(url), # <-- MUDANÇA AQUI
                "departure": "N/A",
                "arrival": "N/A",
                "duration": result.get("title", "Verificar detalhes"),
                "price": "Verificar no site",
                "stops": 0 
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo encontradas na web.")
        return formatted_results

    except Exception as e:
        return [{"id": "error", "airline": f"Erro na busca: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
from typing import List, Dict, Optional
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient # <-- Importar Tavily

class FlightSearchInput(BaseModel):
    origin: str = Field(description="Cidade ou aeroporto de origem.")
    destination: str = Field(description="Cidade ou aeroporto de destino.")
    departure_date: str = Field(description="Data de partida no formato AAAA-MM-DD.")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato AAAA-MM-DD (opcional).")
    passengers: int = Field(default=1, description="Número de passageiros.")

@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, passengers: int = 1) -> List[Dict]:
    """Busca por opções de voos na web com base na origem, destino, datas e número de passageiros."""
    print(f"Tool: Buscando voos REAIS de {origin} para {destination} de {departure_date} {('até ' + return_date) if return_date else ''}...")

    # 1. Inicializar o cliente Tavily
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("Erro: TAVILY_API_KEY não encontrada no .env")
        return [{"id": "error", "airline": "API Key de Busca (Tavily) não configurada", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]

    # 2. Criar a query de busca
    query = f"voos de {origin} para {destination} partindo em {departure_date} e retornando em {return_date} para {passengers} passageiro(s)"

    try:
        # 3. Executar a busca
        search_response = tavily_client.search(
            query=query,
            search_depth="basic",
            include_answer=False,
            max_results=5
        )
        
        web_results = search_response.get("results", [])
        
        # 4. Formatar os resultados
        formatted_results = []
        if not web_results:
             print("Nenhum resultado encontrado na web.")
             return []

        for result in web_results:
            # Mapeamos os resultados da busca para o formato do FlightCard
            formatted_results.append({
                "id": result.get("url"), # Usamos a URL como ID
                "airline": result.get("source", "Fonte desconhecida"), # Ex: skyscanner.com
                "departure": "N/A",
                "arrival": "N/A",
                "duration": result.get("title", "Verificar detalhes"),
                "price": "Verificar no site",
                "stops": 0 # Não temos essa info
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo encontradas na web.")
        return formatted_results

    except Exception as e:
        print(f"Erro ao chamar a API Tavily: {e}")
        return [{"id": "error", "airline": f"Erro na busca: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0}]
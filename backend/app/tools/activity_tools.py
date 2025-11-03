from typing import List, Dict
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient # <-- Importar Tavily

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início das atividades no formato AAAA-MM-DD.")
    end_date: str = Field(description="Data de fim das atividades no formato AAAA-MM-DD.")

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, start_date: str, end_date: str) -> List[Dict]:
    """Busca por atividades e atrações na web no destino para o período especificado."""
    print(f"Tool: Buscando atividades REAIS em {destination} entre {start_date} e {end_date}.")

    # 1. Inicializar o cliente Tavily
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("Erro: TAVILY_API_KEY não encontrada no .env")
        return [{"id": "error", "title": "API Key de Busca (Tavily) não configurada", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]

    # 2. Criar a query de busca
    query = f"atividades, passeios ou 'o que fazer' em {destination} para as datas {start_date} até {end_date}"

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
            # Mapeamos os resultados da busca para o formato do ActivityCard
            formatted_results.append({
                "id": result.get("url"), # Usamos a URL como ID
                "title": result.get("title", "Título não disponível"),
                "description": result.get("content", "Sem descrição..."), # Snippet da busca
                "duration": "N/A", # Não temos essa info da busca
                "price": "Verificar no site", # Não temos preço confiável
                "capacity": result.get("source", "Fonte desconhecida") # Usamos a fonte como "capacidade"
            })
        
        print(f"Retornando {len(formatted_results)} opções de atividade encontradas na web.")
        return formatted_results

    except Exception as e:
        print(f"Erro ao chamar a API Tavily: {e}")
        return [{"id": "error", "title": f"Erro na busca: {e}", "description": "", "duration": "", "price": "R$ 0", "capacity": ""}]
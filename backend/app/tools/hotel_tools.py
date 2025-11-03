from typing import List, Dict, Optional
import os  # <-- Importar OS
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient  # <-- Importar o TavilyClient

class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")
    adults: int = Field(default=1, description="Número de adultos.")
    rooms: int = Field(default=1, description="Número de quartos.")

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> List[Dict]:
    """Busca por opções de hotéis na web com base no destino, datas, número de adultos e quartos."""
    print(f"Tool: Buscando hotéis REAIS em {destination} de {check_in_date} até {check_out_date}...")

    # 1. Inicializar o cliente Tavily
    try:
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except KeyError:
        print("Erro: TAVILY_API_KEY não encontrada no .env")
        return [{"id": "error", "name": "API Key de Busca (Tavily) não configurada no backend", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]

    # 2. Criar a query de busca
    query = f"Opções de hotéis em {destination} para {adults} adultos, de {check_in_date} até {check_out_date}"

    try:
        # 3. Executar a busca
        search_response = tavily_client.search(
            query=query,
            search_depth="basic",  # Usa a busca básica (mais rápida)
            include_answer=False,  # Não precisamos de um resumo da Tavily, só dos resultados
            max_results=5          # Pedimos 5 resultados
        )
        
        web_results = search_response.get("results", [])
        
        # 4. Formatar os resultados da web para o formato esperado pelo app
        formatted_results = []
        if not web_results:
             print("Nenhum resultado encontrado na web.")
             return []

        for result in web_results:
            # Mapeamos os resultados da busca para o formato do HotelCard
            formatted_results.append({
                "id": result.get("url"),  # Usamos a URL como ID
                "name": result.get("title", "Título não disponível"),
                "location": result.get("source", "Fonte desconhecida"), # Ou podemos usar o 'url'
                "rating": 0,  # Não conseguimos extrair rating de forma confiável da busca
                "price": "Verificar no site", # Não conseguimos extrair preço de forma confiável
                "amenities": [result.get("content", "Sem descrição...")] # Usamos o snippet como "amenity"
            })
        
        print(f"Retornando {len(formatted_results)} opções de hotel encontradas na web.")
        return formatted_results

    except Exception as e:
        print(f"Erro ao chamar a API Tavily: {e}")
        return [{"id": "error", "name": f"Erro na busca: {e}", "location": "", "rating": 0, "price": "R$ 0", "amenities": []}]
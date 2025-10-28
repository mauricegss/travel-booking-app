from typing import List, Dict
import random
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino para atividades.")
    start_date: str = Field(description="Data de início das atividades no formato AAAA-MM-DD.")
    end_date: str = Field(description="Data de fim das atividades no formato AAAA-MM-DD.")

@tool(args_schema=ActivitySearchInput)
def search_activities(destination: str, start_date: str, end_date: str) -> List[Dict]:
    """Busca por atividades e atrações no destino para o período especificado."""
    print(f"Tool: Buscando atividades em {destination} entre {start_date} e {end_date}.")

    activity_titles = ["Tour Histórico", "Passeio de Barco", "Visita ao Museu Principal", "Aula de Culinária Local", "Trilha Panorâmica"]
    descriptions = ["Descubra os segredos da cidade.", "Navegue pelas águas locais.", "Explore a arte e a história.", "Aprenda a cozinhar pratos típicos.", "Caminhada com vistas incríveis."]
    durations = ["2h", "3h", "4h", "Meio dia"]
    capacities = ["Até 10 pessoas", "Até 15 pessoas", "Até 20 pessoas", "Grupos pequenos"]
    results = []
    for i in range(random.randint(2, 5)):
        results.append({
            "id": f"activity_{i+1}",
            "title": f"{random.choice(activity_titles)} em {destination}",
            "description": random.choice(descriptions),
            "duration": random.choice(durations),
            "price": f"R$ {random.randint(100, 400)}",
            "capacity": random.choice(capacities)
        })
    print(f"Retornando {len(results)} opções de atividade.")
    return results
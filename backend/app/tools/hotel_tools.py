from typing import List, Dict, Optional
import random
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

class HotelSearchInput(BaseModel):
    destination: str = Field(description="Cidade ou local de destino.")
    check_in_date: str = Field(description="Data de check-in no formato AAAA-MM-DD.")
    check_out_date: str = Field(description="Data de check-out no formato AAAA-MM-DD.")
    adults: int = Field(default=1, description="Número de adultos.")
    rooms: int = Field(default=1, description="Número de quartos.")

@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> List[Dict]:
    """Busca por opções de hotéis com base no destino, datas, número de adultos e quartos."""
    print(f"Tool: Buscando hotéis em {destination} de {check_in_date} até {check_out_date} para {adults} adulto(s) em {rooms} quarto(s).")

    hotel_names = ["Grand Hotel", "Plaza Inn", "Comfort Suites", "Le Jardin Boutique", "Ocean View Resort"]
    locations = ["Centro", "Próximo à Praia", "Bairro Nobre", "Perto do Aeroporto", "Zona Histórica"]
    amenities_options = [["wifi"], ["wifi", "breakfast"], ["wifi", "pool"], ["wifi", "breakfast", "gym"]]
    results = []
    for i in range(random.randint(3, 6)):
        rating = random.randint(3, 5)
        price_per_night = random.randint(250, 900)

        results.append({
            "id": f"hotel_{i+1}",
            "name": f"{random.choice(hotel_names)} {destination}",
            "location": random.choice(locations),
            "rating": rating,
            "price": f"R$ {price_per_night * rooms}",
            "amenities": random.choice(amenities_options)
        })
    print(f"Retornando {len(results)} opções de hotel.")
    return results
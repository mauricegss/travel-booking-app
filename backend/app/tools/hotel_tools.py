from typing import List, Dict
import random

def search_hotels(destination: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> List[Dict]:
    print(f"Buscando hotéis em {destination} de {check_in_date} até {check_out_date} para {adults} adulto(s) em {rooms} quarto(s).")

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
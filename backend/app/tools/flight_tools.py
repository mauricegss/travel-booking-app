from typing import List, Dict, Optional
import random

def search_flights(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, passengers: int = 1) -> List[Dict]:
    print(f"Buscando voos de {origin} para {destination} de {departure_date} {('até ' + return_date) if return_date else ''} para {passengers} passageiro(s).")

    airlines = ["LATAM", "Azul", "Gol", "Air France", "KLM"]
    results = []
    for i in range(random.randint(2, 5)):
        dep_hour = random.randint(5, 20)
        dep_min = random.choice([0, 15, 30, 45])
        duration_hours = random.randint(8, 15)
        duration_min = random.choice([0, 15, 30, 45])
        arrival_hour = (dep_hour + duration_hours) % 24
        arrival_min = (dep_min + duration_min) % 60 # Simplificado
        stops = random.choice([0, 1, 2])

        results.append({
            "id": f"flight_{i+1}",
            "airline": random.choice(airlines),
            "departure": f"{dep_hour:02d}:{dep_min:02d}",
            "arrival": f"{arrival_hour:02d}:{arrival_min:02d}",
            "duration": f"{duration_hours}h {duration_min}m",
            "price": f"R$ {random.randint(1800, 3500) * passengers}",
            "stops": stops
        })
    print(f"Retornando {len(results)} opções de voo.")
    return results
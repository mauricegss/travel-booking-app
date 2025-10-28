# backend/app/tools/flight_tools.py
from typing import List, Dict, Optional
import random
from langchain_core.tools import tool # Importar o decorador @tool
from pydantic.v1 import BaseModel, Field # Usar Pydantic para definir o schema de entrada

# Definir um schema Pydantic para a entrada da ferramenta (melhora a robustez)
class FlightSearchInput(BaseModel):
    origin: str = Field(description="Cidade ou aeroporto de origem.")
    destination: str = Field(description="Cidade ou aeroporto de destino.")
    departure_date: str = Field(description="Data de partida no formato AAAA-MM-DD.")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato AAAA-MM-DD (opcional).")
    passengers: int = Field(default=1, description="Número de passageiros.")

@tool(args_schema=FlightSearchInput) # Usar o decorador e o schema
def search_flights(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, passengers: int = 1) -> List[Dict]:
    """Busca por opções de voos com base na origem, destino, datas e número de passageiros.""" # Docstring é a descrição da ferramenta!
    print(f"LangChain Tool: Buscando voos de {origin} para {destination} de {departure_date} {('até ' + return_date) if return_date else ''} para {passengers} passageiro(s).")

    # ... (lógica da função permanece a mesma) ...
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

# Faça o mesmo para hotel_tools.py e activity_tools.py, usando @tool e definindo schemas Pydantic se desejar.
# Lembre-se de adicionar docstrings descritivas!
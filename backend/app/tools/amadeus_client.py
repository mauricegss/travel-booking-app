import os
from amadeus import Client, ResponseError
from functools import lru_cache
from typing import Dict 
from unidecode import unidecode 

try:
    amadeus = Client(
        client_id=os.environ["AMADEUS_API_KEY"],
        client_secret=os.environ["AMADEUS_API_SECRET"],
        hostname='test' 
    )
    print("Cliente Amadeus inicializado no modo TESTE.")
except KeyError:
    print("ERRO: AMADEUS_API_KEY ou AMADEUS_API_SECRET não encontradas. Verifique se o .env foi carregado ANTES deste import.")
    amadeus = None

@lru_cache(maxsize=100)
def get_location_data(city_name: str) -> Dict | None:
    if not amadeus:
        print("ERRO: Cliente Amadeus (global) não está inicializado.")
        return None
        
    normalized_city_name = unidecode(city_name) 
    print(f"Buscando IATA/GeoCode para: {city_name} (Normalizado: {normalized_city_name})")

    try:
        response = amadeus.reference_data.locations.get(
            keyword=normalized_city_name,
            subType='CITY,AIRPORT'
        )
        
        # --- INÍCIO DA CORREÇÃO ---
        # Verifica se a lista de dados não está vazia antes de aceder ao índice
        if not response.data:
            print(f"Nenhum resultado de localização encontrado para {city_name}")
            return None
        # --- FIM DA CORREÇÃO ---
            
        data = response.data[0]
        return {
            "iataCode": data.get('iataCode'),
            "geoCode": data.get('geoCode'),
            "name": data.get('name')
        }
    except (ResponseError, IndexError, KeyError) as e:
        print(f"Erro ao buscar IATA para {city_name}: {e}")
        return None

# O bloco de teste if __name__ == "__main__" pode continuar igual
if __name__ == "__main__":
    if 'AMADEUS_API_KEY' not in os.environ:
         print("Variáveis de ambiente não carregadas. Tentando carregar .env para teste...")
         from dotenv import load_dotenv
         dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
         load_dotenv(dotenv_path=dotenv_path)
         
         try:
            amadeus = Client(
                client_id=os.environ["AMADEUS_API_KEY"],
                client_secret=os.environ["AMADEUS_API_SECRET"],
                hostname='test'
            )
            print("Cliente Amadeus reinicializado para teste.")
         except KeyError:
             print("ERRO CRÍTICO: Chaves Amadeus não encontradas. Verifique seu arquivo .env.")
             exit()

    location_sp = get_location_data("São Paulo")
    print(f"Teste São Paulo: {location_sp}")
    
    location_par = get_location_data("Paris")
    print(f"Teste Paris: {location_par}")
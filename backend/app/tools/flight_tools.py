from typing import List, Dict, Optional
import os
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from serpapi import GoogleSearch
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import lru_cache
from app.tools.image_tools import search_image # <-- IMPORTAR FERRAMENTA DE IMAGEM

# --- O Helper de IATA (Gemini) ---
@lru_cache(maxsize=100)
def _get_iata_code(city_name: str) -> dict | None:
    print(f"Tool (Voo-Helper): Buscando IATA para {city_name} usando Gemini 2.5 Flash...")
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        
        prompt = f"""
        Você é um especialista em aviação comercial.
        A partir da cidade '{city_name}', qual é o aeroporto comercial DE GRANDE PORTE (HUB nacional/internacional) mais próximo que opera várias companhias e voos diários?
        ATENÇÃO: Ignore aeroportos regionais pequenos, fazendas ou aeroclubes que não possuem malha ativa pesada.
        Exemplo: Para Ponta Grossa, o correto é Curitiba CWB. Para Niterói, o correto é Rio de Janeiro GIG ou SDU.
        
        Responda APENAS com um objeto JSON estrito no seguinte formato:
        {{"iataCode": "XXX", "cityName": "Nome real da cidade do Aeroporto", "isFallback": true_se_a_cidade_do_aeroporto_for_diferente_da_origem}}
        """
        
        response = llm.invoke(prompt)
        text = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        if data.get('iataCode'):
            iata = data['iataCode']
            city = data.get('cityName', city_name)
            is_fallback = data.get('isFallback', False)
            print(f"IATA Code extraído via Gemini: {iata} (Cidade: {city}, Fallback: {is_fallback})")
            return {"iata": iata, "city": city, "isFallback": is_fallback}
            
    except Exception as e:
        print(f"Erro ao processar IATA com Gemini: {e}")
        
    return None
# --- Fim do Helper ---


class FlightSearchInput(BaseModel):
    origin: str = Field(description="Cidade ou aeroporto de origem.")
    destination: str = Field(description="Cidade ou aeroporto de destino.")
    departure_date: str = Field(description="Data de partida no formato AAAA-MM-DD.")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato AAAA-MM-DD (opcional).")
    passengers: int = Field(default=1, description="Número de passageiros.")

@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, departure_date: str, **kwargs) -> List[Dict]:
    """Busca por voos usando a API Google Flights da SerpAPI e anexa uma imagem da companhia."""
    print(f"Tool: Buscando voos REAIS (SerpAPI Google Flights) de {origin} para {destination}...")
    
    return_date = kwargs.get('return_date')
    passengers = kwargs.get('passengers', 1)

    try:
        SERPAPI_KEY = os.environ["SERPAPI_API_KEY"]
        if "TAVILY_API_KEY" not in os.environ:
            raise KeyError("TAVILY_API_KEY não configurada no .env")
            
    except KeyError as e:
        error_msg = f"{e.args[0]} não configurada."
        return [{"id": "error", "airline": error_msg, "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0, "image_url": None}]

    origin_data = _get_iata_code(origin)
    dest_data = _get_iata_code(destination)

    if not origin_data:
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para a origem: {origin}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0, "image_url": None}]
    if not dest_data:
        return [{"id": "error", "airline": f"Não foi possível encontrar o código IATA para o destino: {destination}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0, "image_url": None}]

    origin_iata = origin_data["iata"]
    dest_iata = dest_data["iata"]
    
    fallback_note = ""
    if origin_data.get("isFallback"):
        fallback_note += f"A origem {origin} não possui aeroporto principal, buscamos por {origin_data.get('city', origin_iata)} ({origin_iata}). "
    if dest_data.get("isFallback"):
        fallback_note += f"O destino {destination} não possui aeroporto principal, buscamos por {dest_data.get('city', dest_iata)} ({dest_iata})."
    
    params = {
        "engine": "google_flights",
        "api_key": SERPAPI_KEY,
        "departure_id": origin_iata,
        "arrival_id": dest_iata,
        "outbound_date": departure_date,
        "adults": passengers,
        "currency": "BRL",
        "hl": "pt-br",
        "gl": "br"
    }

    if return_date:
        params["return_date"] = return_date

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            error_msg = results["error"]
            print(f"!!! Erro da SerpAPI (Voos): {error_msg}")
            return [{"id": "error", "airline": f"Erro na API de voos: {error_msg}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0, "image_url": None}]

        formatted_results = []
        data_to_parse = results.get("best_flights", [])
        
        if not data_to_parse:
            data_to_parse = results.get("other_flights", [])

        if not data_to_parse:
            print("SerpAPI não retornou 'best_flights' ou 'other_flights', mas não reportou erro.")
            return []

        for flight in data_to_parse:
            legs = flight.get("flights", [])
            if not legs:
                continue 

            outbound_leg = legs[0]
            dep_airport = outbound_leg.get("departure_airport", {}).get("id", origin_iata)
            arr_airport = outbound_leg.get("arrival_airport", {}).get("id", dest_iata)
            
            # Extract just the HH:MM from '2026-03-25 14:30'
            dep_raw = outbound_leg.get('departure_airport', {}).get('time', 'N/A')
            dep_time_str = dep_raw.split(" ")[1] if " " in dep_raw else dep_raw
            
            arr_raw = outbound_leg.get('arrival_airport', {}).get('time', 'N/A')
            arr_time_str = arr_raw.split(" ")[1] if " " in arr_raw else arr_raw
            
            departure_time = f"{dep_time_str} ({dep_airport})"
            arrival_time = f"{arr_time_str} ({arr_airport})"

            if return_date and len(legs) > 1:
                return_leg = legs[1]
                ret_dep_airport = return_leg.get("departure_airport", {}).get("id", dest_iata)
                
                # Para mostrar Ida e Volta mantemos apenas origem -> destino (já que é só Partida/Chegada na UI)
                # O usuário pediu expressamente pra tirar Ida e Volta e deixar apenas o horário
                ret_dep_raw = return_leg.get('departure_airport', {}).get('time', 'N/A')
                ret_dep_time_str = ret_dep_raw.split(" ")[1] if " " in ret_dep_raw else ret_dep_raw
                
                departure_time = f"{dep_time_str} ({dep_airport})"
                arrival_time = f"{ret_dep_time_str} ({ret_dep_airport})"
            
            # Formatar a duração para "Xh Ym"
            duration_raw = flight.get("total_duration")
            try:
                duration_min = int(duration_raw)
                h = duration_min // 60
                m = duration_min % 60
                formatted_duration = f"{h}h {m}m" if m > 0 else f"{h}h"
            except (ValueError, TypeError):
                formatted_duration = f"{duration_raw} min" if duration_raw else 'N/A'

            # --- NOVA ADIÇÃO: BUSCAR IMAGEM DA COMPANHIA ---
            # (Usamos o nome da companhia + "logo" para melhores resultados)
            image_url = search_image.invoke({"query": f"{airline_name} logo aviacion"})
            # ----------------------------------------------

            formatted_results.append({
                "id": flight.get("google_flights_url", "default_id"),
                "airline": airline_name,
                "departure": departure_time,
                "arrival": arrival_time,
                "duration": formatted_duration,
                "price": f"R$ {flight.get('price', 0)}", 
                "stops": flight.get("stops", 0),
                "image_url": image_url, # <-- ANEXAR A IMAGEM
                "fallback_note": fallback_note.strip() if fallback_note else None
            })
        
        print(f"Retornando {len(formatted_results)} opções de voo da SerpAPI (com imagens).")
        return formatted_results[:10]

    except Exception as e:
        print(f"Erro inesperado (Voos - SerpAPI): {e}")
        return [{"id": "error", "airline": f"Erro ao buscar voos na SerpAPI: {e}", "departure": "", "arrival": "", "duration": "", "price": "R$ 0", "stops": 0, "image_url": None}]
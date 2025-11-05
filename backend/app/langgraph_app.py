import os
from dotenv import load_dotenv

# --- CARREGUE O .ENV PRIMEIRO DE TUDO ---
# Isso garante que 'os.environ' tenha as chaves ANTES do amadeus_client ser importado
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)
print(f".env carregado de {dotenv_path}")
# --- FIM DA MUDANÇA ---

from typing import TypedDict, Annotated, List, Dict
import operator
import re
from langchain_core.exceptions import OutputParserException

from pydantic import BaseModel, Field as PydanticV2Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from langgraph.graph import StateGraph, END

# Agora estes imports podem usar o os.environ que foi carregado acima
from app.tools.flight_tools import search_flights
from app.tools.hotel_tools import search_hotels
from app.tools.activity_tools import search_activities


if 'GOOGLE_API_KEY' not in os.environ:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
    # (Não vamos sair, mas o LLM pode falhar)
else:
    print("GOOGLE_API_KEY carregada com sucesso.")


try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, convert_system_message_to_human=True)
    print("Modelo ChatGoogleGenerativeAI inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o ChatGoogleGenerativeAI: {e}")
    exit()

# --- Modelos Pydantic V2 ---
class FlightDetails(BaseModel):
    id: str = PydanticV2Field(description="Identificador único do voo")
    airline: str = PydanticV2Field(description="Nome da companhia aérea")
    departure: str = PydanticV2Field(description="Horário de partida")
    arrival: str = PydanticV2Field(description="Horário de chegada")
    duration: str = PydanticV2Field(description="Duração total do voo")
    price: str = PydanticV2Field(description="Preço total do voo")
    stops: int = PydanticV2Field(description="Número de paradas")

class HotelDetails(BaseModel):
    id: str = PydanticV2Field(description="Identificador único do hotel")
    name: str = PydanticV2Field(description="Nome do hotel")
    location: str = PydanticV2Field(description="Localização ou bairro do hotel")
    rating: int = PydanticV2Field(description="Avaliação do hotel (ex: 3, 4, 5 estrelas)")
    price: str = PydanticV2Field(description="Preço médio por noite")
    amenities: List[str] = PydanticV2Field(description="Lista de comodidades oferecidas")

class ActivityDetails(BaseModel):
    id: str = PydanticV2Field(description="Identificador único da atividade")
    title: str = PydanticV2Field(description="Título da atividade")
    description: str = PydanticV2Field(description="Breve descrição da atividade")
    duration: str = PydanticV2Field(description="Duração estimada da atividade")
    price: str = PydanticV2Field(description="Preço por pessoa")
    capacity: str = PydanticV2Field(description="Capacidade ou tamanho do grupo")

class ExtractedInfo(BaseModel):
    origin: str | None = PydanticV2Field(None, description="Cidade ou local de origem da viagem.")
    destination: str | None = PydanticV2Field(None, description="Cidade ou local de destino principal.")
    start_date: str | None = PydanticV2Field(None, description="Data de início da viagem no formato AAAA-MM-DD.")
    end_date: str | None = PydanticV2Field(None, description="Data de fim da viagem no formato AAAA-MM-DD.")

class TravelAppState(TypedDict):
    user_request: str
    origin: str | None 
    destination: str | None
    start_date: str | None
    end_date: str | None
    flights: List[Dict] | None
    hotels: List[Dict] | None
    activities: List[Dict] | None
    itinerary: str
    error: str | None


def extract_info_node(state: TravelAppState) -> dict:
    print("--- 🔍 Extraindo Informações da Requisição ---")
    user_request = state['user_request']

    parser = PydanticOutputParser(pydantic_object=ExtractedInfo)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente especialista em extrair informações de viagem de texto. Extraia a origem, o destino principal, data de início (check-in) e data de fim (check-out) do pedido do usuário. Se alguma informação não estiver clara ou ausente, retorne null para o campo correspondente. Use o formato AAAA-MM-DD para datas.\n{format_instructions}"),
        ("human", "{user_request}")
    ])

    chain = prompt | llm | parser

    try:
        extracted: ExtractedInfo = chain.invoke({
            "user_request": user_request,
            "format_instructions": parser.get_format_instructions()
        })
        print(f"Informações extraídas: Origem={extracted.origin}, Destino={extracted.destination}, Início={extracted.start_date}, Fim={extracted.end_date}")

        error_msg = None
        if not extracted.origin or not extracted.destination or not extracted.start_date or not extracted.end_date:
             error_msg = "Não foi possível extrair origem, destino e/ou datas completas. Por favor, especifique claramente."
             print(f"Erro na extração: {error_msg}")

        return {
            "origin": extracted.origin,
            "destination": extracted.destination,
            "start_date": extracted.start_date,
            "end_date": extracted.end_date,
            "error": error_msg
        }
    except Exception as e:
        print(f"Erro crítico ao extrair informações: {e}")
        origin_match = re.search(r"(?:de|saindo de)\s+([A-Z][a-zA-Z\s,]+)", user_request)
        dest_match = re.search(r"(?:para|a|em)\s+([A-Z][a-zA-Z\s,]+)", user_request)
        origin_fb = origin_match.group(1).strip().rstrip(',') if origin_match else None
        dest_fb = dest_match.group(1).strip().rstrip(',') if dest_match else None
        error_msg = f"Não foi possível processar a extração automaticamente. Verifique o pedido. Erro: {e}"
        return {
            "origin": origin_fb,
            "destination": dest_fb,
            "start_date": None,
            "end_date": None,
            "error": error_msg
        }


def flight_agent_node(state: TravelAppState) -> dict:
    print("--- ✈️ Agente de Voos: Chamando ferramenta ---")
    origin = state.get("origin")
    dest = state.get("destination")
    start = state.get("start_date")
    end = state.get("end_date")
    current_error = state.get("error")

    if not origin or not dest or not start or not end or current_error:
         error_msg = current_error or "Origem, destino ou datas ausentes para busca de voos."
         print(f"Erro voos: {error_msg}")
         return {"flights": [], "error": error_msg}

    try:
        results = search_flights.invoke({
            "origin": origin,
            "destination": dest,
            "departure_date": start,
            "return_date": end,
            "passengers": 1
        })
        return {"flights": results, "error": None} # Remove o erro anterior se a busca for bem sucedida
    except Exception as e:
        print(f"Erro ao chamar ferramenta de voos: {e}")
        return {"flights": [], "error": f"Erro ao buscar voos: {e}"}

def hotel_agent_node(state: TravelAppState) -> dict:
    print("--- 🏨 Agente de Hospedagem: Chamando ferramenta ---")
    dest = state.get("destination")
    start = state.get("start_date")
    end = state.get("end_date")
    current_error = state.get("error") # Propaga erro, se houver

    if not dest or not start or not end or current_error:
        error_msg = current_error or "Destino ou datas ausentes para busca de hotéis."
        print(f"Erro hotéis: {error_msg}")
        return {"hotels": [], "error": error_msg}

    try:
        results = search_hotels.invoke({
            "destination": dest,
            "check_in_date": start,
            "check_out_date": end
        })
        return {"hotels": results, "error": state.get("error")}
    except Exception as e:
        print(f"Erro ao chamar ferramenta de hotéis: {e}")
        error_msg = f"{current_error + '; ' if current_error else ''}Erro ao buscar hotéis: {e}"
        return {"hotels": [], "error": error_msg}


def activity_agent_node(state: TravelAppState) -> dict:
    print("--- 🗺️ Agente de Atividades: Chamando ferramenta ---")
    dest = state.get("destination")
    start = state.get("start_date")
    end = state.get("end_date")
    current_error = state.get("error") # Propaga erro

    if not dest or not start or not end or current_error:
        error_msg = current_error or "Destino ou datas ausentes para busca de atividades."
        print(f"Erro atividades: {error_msg}")
        return {"activities": [], "error": error_msg}

    try:
        results = search_activities.invoke({
            "destination": dest,
            "start_date": start,
            "end_date": end
        })
        return {"activities": results, "error": state.get("error")}
    except Exception as e:
        print(f"Erro ao chamar ferramenta de atividades: {e}")
        error_msg = f"{current_error + '; ' if current_error else ''}Erro ao buscar atividades: {e}"
        return {"activities": [], "error": error_msg}

def format_list_of_dicts(data: List[Dict] | None, title: str) -> str:
    if not data or (len(data) == 1 and data[0].get('id') == 'error'):
        return f"\n**{title}:**\nNenhuma opção encontrada ou erro na busca.\n"
    output = f"\n**{title}:**\n"
    for idx, item in enumerate(data):
        output += f"- Opção {idx+1}:\n"
        for key, value in item.items():
            if key != 'id': # Não mostra o 'id' (que é um link) no resumo
                 output += f"  - {key.replace('_', ' ').capitalize()}: {value}\n"
    return output

def integration_agent_node(state: TravelAppState) -> dict:
    print("--- 🧾 Agente de Integração: Montando o itinerário final ---")

    initial_error = state.get("error")
    found_flights = state.get("flights")
    found_hotels = state.get("hotels")
    found_activities = state.get("activities")

    if initial_error and not found_flights and not found_hotels and not found_activities:
         print(f"Retornando erro inicial: {initial_error}")
         return {
            "itinerary": f"Erro no planejamento: {initial_error}\nPor favor, tente refazer a busca com mais detalhes.",
            "flights": [], "hotels": [], "activities": [],
            "origin": state.get("origin"), "destination": state.get("destination"),
            "start_date": state.get("start_date"), "end_date": state.get("end_date")
         }

    flights_str = format_list_of_dicts(found_flights, "Opções de Voos")
    hotels_str = format_list_of_dicts(found_hotels, "Opções de Hotéis")
    activities_str = format_list_of_dicts(found_activities, "Sugestões de Atividades")

    error_parts = []
    if initial_error: # Erro da extração
        error_parts.append(initial_error)
    
    # Verifica se os resultados não são apenas a mensagem de erro da ferramenta
    if not found_flights or (len(found_flights) == 1 and found_flights[0].get('id') == 'error'):
        error_parts.append("Não foi possível buscar voos.")
    if not found_hotels or (len(found_hotels) == 1 and found_hotels[0].get('id') == 'error'):
        error_parts.append("Não foi possível buscar hotéis.")
    if not found_activities or (len(found_activities) == 1 and found_activities[0].get('id') == 'error'):
        error_parts.append("Não foi possível buscar atividades.")

    error_str = f"\n**Avisos:**\n- {'\n- '.join(error_parts)}\n" if error_parts else ""


    summary_prompt = f"""
    Você é o agente de integração mestre. Sua tarefa é pegar as informações
    coletadas pelos outros agentes e apresentá-las ao usuário de forma clara,
    organizada e amigável, como um plano de viagem inicial.

    O pedido original do usuário foi:
    {state['user_request']}

    Origem: {state.get('origin', 'Não extraída')}
    Destino: {state.get('destination', 'Não extraído')}
    Período: {state.get('start_date', 'Não extraído')} a {state.get('end_date', 'Não extraído')}

    {flights_str}
    {hotels_str}
    {activities_str}
    {error_str}

    Compile tudo isso em um único itinerário. Adicione uma saudação amigável no início
    e uma frase de encerramento (ex: "Espero que goste das opções! Se precisar ajustar algo, me diga.").
    Mencione brevemente se alguma das seções não teve resultados ou apresentou erro.
    """

    print("--- 🤖 Formatando o itinerário completo... ---")

    chain = llm | StrOutputParser()
    response = chain.invoke(summary_prompt)

    return {
        "itinerary": response,
        "flights": found_flights or [],
        "hotels": found_hotels or [],
        "activities": found_activities or [],
        "origin": state.get("origin"),
        "destination": state.get("destination"),
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "error": initial_error or (error_str if error_str else None)
    }

# --- Definição do Grafo (sem mudanças) ---
print("Construindo o gráfico de agentes LangGraph...")
workflow = StateGraph(TravelAppState)
workflow.add_node("extract_info", extract_info_node)
workflow.add_node("flights", flight_agent_node)
workflow.add_node("hotels", hotel_agent_node)
workflow.add_node("activities", activity_agent_node)
workflow.add_node("integrator", integration_agent_node)
workflow.set_entry_point("extract_info")
workflow.add_edge("extract_info", "flights")
workflow.add_edge("flights", "hotels")
workflow.add_edge("hotels", "activities")
workflow.add_edge("activities", "integrator")
workflow.add_edge("integrator", END)
app = workflow.compile()
print("Gráfico compilado com sucesso.")

# --- Execução __main__ (sem mudanças) ---
if __name__ == "__main__":
    print("\n--- Iniciando Planejamento da Viagem (Execução Direta) ---")
    user_input = "Planeje uma viagem de São Paulo para Paris de 2026-05-10 até 2026-05-17"
    initial_state = TravelAppState( user_request= user_input, origin=None, destination= None, start_date= None, end_date= None, flights= None, hotels= None, activities= None, itinerary= "", error= None )
    try:
        final_response_state = app.invoke(initial_state)
        print("\n--- Planejamento Concluído! ---")
        print("\n" + "="*50)
        print("             ITINERÁRIO FINAL GERADO")
        print("="*50 + "\n")
        print(final_response_state.get('itinerary', "Nenhum itinerário gerado."))
        print("\n--- Dados Brutos ---")
        print("Origem:", final_response_state.get('origin'))
        print("Destino:", final_response_state.get('destination'))
        print("Início:", final_response_state.get('start_date'))
        print("Fim:", final_response_state.get('end_date'))
        print("Voos:", final_response_state.get('flights'))
        print("Hotéis:", final_response_state.get('hotels'))
        print("Atividades:", final_response_state.get('activities'))
        print("Erro:", final_response_state.get('error'))
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"\nErro durante a execução do gráfico: {e}")
        import traceback
        traceback.print_exc()
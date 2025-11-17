import os
from dotenv import load_dotenv
import json # <-- IMPORTAR JSON

# --- CARREGUE O .ENV PRIMEIRO DE TUDO ---
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

# --- Modelos Pydantic V2 (Sem alterações) ---
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

# --- Nó de Extração (Sem alterações) ---
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

# --- Agentes de Busca (Sem alterações) ---
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

# --- REMOVEMOS A FUNÇÃO ANTIGA format_list_of_dicts ---


# --- MUDANÇA PRINCIPAL: O NOVO AGENTE CURADOR/INTEGRADOR ---
def curate_and_report_node(state: TravelAppState) -> dict:
    print("--- 🧠 Agente Curador: Analisando e selecionando os melhores resultados ---")

    initial_error = state.get("error")
    
    # Filtra resultados que são erros
    def filter_errors(results: List[Dict] | None) -> List[Dict]:
        if not results:
            return []
        return [item for item in results if item.get("id") != "error"]

    found_flights = filter_errors(state.get("flights"))
    found_hotels = filter_errors(state.get("hotels"))
    found_activities = filter_errors(state.get("activities"))

    # Converte os resultados limpos para JSON para enviar ao LLM
    flights_json = json.dumps(found_flights, indent=2, ensure_ascii=False)
    hotels_json = json.dumps(found_hotels, indent=2, ensure_ascii=False)
    activities_json = json.dumps(found_activities, indent=2, ensure_ascii=False)

    # Se houver um erro de extração e NENHUMA ferramenta retornou dados, encerra
    if initial_error and not found_flights and not found_hotels and not found_activities:
         print(f"Retornando erro inicial: {initial_error}")
         return {
            "itinerary": f"Erro no planejamento: {initial_error}\nPor favor, tente refazer a busca com mais detalhes.",
            "flights": [], "hotels": [], "activities": [],
            "origin": state.get("origin"), "destination": state.get("destination"),
            "start_date": state.get("start_date"), "end_date": state.get("end_date"),
            "error": initial_error
         }

    # <<< INÍCIO DA MUDANÇA (PROMPT ATUALIZADO) >>>
    # Este é o novo prompt "inteligente" ATUALIZADO
    summary_prompt = f"""
    Você é um agente de viagens especialista e seu trabalho é criar um "Relatório de Recomendações"
    para um usuário. Você recebeu dados brutos de ferramentas de busca e agora deve analisá-los,
    selecionar as melhores opções e justificar suas escolhas.

    O pedido original do usuário foi:
    "{state['user_request']}"

    Informações da Viagem:
    Origem: {state.get('origin', 'Não extraída')}
    Destino: {state.get('destination', 'Não extraído')}
    Período: {state.get('start_date', 'Não extraído')} a {state.get('end_date', 'Não extraído')}

    --- DADOS BRUTOS DAS FERRAMENTAS ---

    Opções de Voos Encontradas:
    {flights_json}

    Opções de Hotéis Encontradas:
    {hotels_json}

    Opções de Atividades Encontradas:
    {activities_json}

    --- SEU RELATÓRIO DE RECOMENDAÇÃO ---

    Sua tarefa é gerar um relatório em Markdown (use #, ##, * e -) que:
    1.  Comece com uma saudação amigável e um resumo da viagem.
    2.  Analise as listas JSON acima.
    3.  Selecione as **melhores 1-2 opções de voos**. Justifique (ex: "Melhor rota").
        **Formate a recomendação como um link clicável usando o campo 'id'**: `* [Companhia Aérea: Preço](link_do_id) - Justificativa.`
    4.  Selecione as **melhores 3 opções de hotéis**. Justifique (ex: "Ótima localização").
        **Formate a recomendação como um link clicável usando o campo 'id'**: `* [Nome do Hotel: Preço](link_do_id) - Justificativa.`
    5.  Selecione as **melhores 4-5 atividades** para criar um roteiro variado. Justifique (ex: "Imperdível").
        **Formate a recomendação como um link clicável usando o campo 'id'**: `* [Nome da Atividade](link_do_id) - Justificativa.`
    6.  Se alguma categoria não tiver resultados (lista vazia), informe ao usuário amigavelmente (ex: "Não encontrei voos para este período, mas veja os hotéis...").
    7.  Termine com uma frase de encerramento.

    O foco é na **QUALIDADE** da seleção, não na quantidade. Pense como um agente de viagens real.

    Comece o relatório:
    """
    # <<< FIM DA MUDANÇA (PROMPT ATUALIZADO) >>>

    print("--- 🤖 Gerando relatório de recomendações com o Gemini... ---")

    chain = llm | StrOutputParser()
    report = chain.invoke(summary_prompt)

    # Retorna o relatório (itinerary) e TAMBÉM as listas filtradas
    return {
        "itinerary": report,
        "flights": found_flights,
        "hotels": found_hotels,
        "activities": found_activities,
        "origin": state.get("origin"),
        "destination": state.get("destination"),
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "error": initial_error
    }


# --- Definição do Grafo (ATUALIZADO) ---
print("Construindo o gráfico de agentes LangGraph...")
workflow = StateGraph(TravelAppState)
workflow.add_node("extract_info", extract_info_node)
workflow.add_node("flights", flight_agent_node)
workflow.add_node("hotels", hotel_agent_node)
workflow.add_node("activities", activity_agent_node)
# Renomeamos o último nó para refletir sua nova função
workflow.add_node("curate_and_report", curate_and_report_node) 

workflow.set_entry_point("extract_info")
workflow.add_edge("extract_info", "flights")
workflow.add_edge("flights", "hotels")
workflow.add_edge("hotels", "activities")
# A borda final agora aponta para o novo nó curador
workflow.add_edge("activities", "curate_and_report")
workflow.add_edge("curate_and_report", END)

app = workflow.compile()
print("Gráfico compilado com sucesso.")

# --- Execução __main__ (sem mudanças) ---
if __name__ == "__main__":
    print("\n--- Iniciando Planejamento da Viagem (Execução Direta) ---")
    user_input = "Planeje uma viagem de São Paulo para Curitiba de 2025-12-10 até 2025-12-17"
    initial_state = TravelAppState( user_request= user_input, origin=None, destination= None, start_date= None, end_date= None, flights= None, hotels= None, activities= None, itinerary= "", error= None )
    try:
        final_response_state = app.invoke(initial_state)
        print("\n--- Planejamento Concluído! ---")
        print("\n" + "="*50)
        print("             RELATÓRIO FINAL GERADO")
        print("="*50 + "\n")
        print(final_response_state.get('itinerary', "Nenhum itinerário gerado."))
        print("\n--- Dados Brutos (Filtrados) ---")
        print("Voos:", final_response_state.get('flights'))
        print("Hotéis:", final_response_state.get('hotels'))
        print("Atividades:", final_response_state.get('activities'))
        print("Erro:", final_response_state.get('error'))
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"\nErro durante a execução do gráfico: {e}")
        import traceback
        traceback.print_exc()
import os
from dotenv import load_dotenv
import json 

# --- CARREGUE O .ENV ---
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)
print(f".env carregado de {dotenv_path}")
# --- FIM ---

from typing import TypedDict, Annotated, List, Dict, Any
import operator
import re
from langchain_core.exceptions import OutputParserException
from datetime import datetime

from pydantic import BaseModel, Field as PydanticV2Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from langgraph.graph import StateGraph, END

# Importar TODAS as ferramentas
from app.tools.flight_tools import search_flights
from app.tools.hotel_tools import search_hotels
from app.tools.activity_tools import search_activities
from app.tools.image_tools import search_image # <-- Importar a ferramenta de imagem (embora a usemos dentro das outras)


if 'GOOGLE_API_KEY' not in os.environ:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
else:
    print("GOOGLE_API_KEY carregada com sucesso.")


try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, convert_system_message_to_human=True)
    print("Modelo ChatGoogleGenerativeAI inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o ChatGoogleGenerativeAI: {e}")
    exit()

# --- Modelos Pydantic V2 (Definições de dados) ---
# (Estes são os mesmos de antes, mas agora vamos usá-los no PydanticOutputParser)
class FlightDetails(BaseModel):
    id: str = PydanticV2Field(description="Identificador único do voo")
    airline: str = PydanticV2Field(description="Nome da companhia aérea")
    departure: str = PydanticV2Field(description="Horário de partida")
    arrival: str = PydanticV2Field(description="Horário de chegada")
    duration: str = PydanticV2Field(description="Duração total do voo")
    price: str = PydanticV2Field(description="Preço total do voo")
    stops: int = PydanticV2Field(description="Número de paradas")

class HotelDetails(BaseModel):
    id: str = PydanticV2Field(description="Identificador único do hotel (geralmente um link)")
    name: str = PydanticV2Field(description="Nome do hotel")
    location: str = PydanticV2Field(description="Localização ou bairro do hotel")
    rating: int = PydanticV2Field(description="Avaliação do hotel (ex: 3, 4, 5 estrelas)")
    price: str = PydanticV2Field(description="Preço (pode ser 'Verificar no site')")
    amenities: List[str] = PydanticV2Field(description="Lista de comodidades oferecidas")
    image_url: str | None = PydanticV2Field(description="URL de uma imagem do hotel")

class ActivityDetails(BaseModel):
    id: str = PydanticV2Field(description="Identificador único da atividade (geralmente um link)")
    title: str = PydanticV2Field(description="Título da atividade")
    description: str = PydanticV2Field(description="Breve descrição da atividade")
    duration: str = PydanticV2Field(description="Duração estimada da atividade")
    price: str = PydanticV2Field(description="Preço por pessoa")
    capacity: str = PydanticV2Field(description="Fonte da atividade (ex: Tourism, Leisure)")
    image_url: str | None = PydanticV2Field(description="URL de uma imagem da atividade")

class ExtractedInfo(BaseModel):
    origin: str | None = PydanticV2Field(None, description="Cidade ou local de origem da viagem.")
    destination: str | None = PydanticV2Field(None, description="Cidade ou local de destino principal.")
    start_date: str | None = PydanticV2Field(None, description="Data de início da viagem no formato AAAA-MM-DD.")
    end_date: str | None = PydanticV2Field(None, description="Data de fim da viagem no formato AAAA-MM-DD.")

# --- NOVOS MODELOS PARA A RESPOSTA CURADA ---

class CuratedRecommendation(BaseModel):
    """Um item (voo, hotel ou atividade) selecionado com uma justificativa."""
    data: Dict[str, Any] = PydanticV2Field(description="O objeto JSON original completo do item (voo, hotel ou atividade).")
    justification: str = PydanticV2Field(description="Breve justificativa (1-2 frases) do porquê este item foi recomendado.")

class FinalReport(BaseModel):
    """O relatório final estruturado contendo as seleções curadas e texto de apoio."""
    summary_text: str = PydanticV2Field(description="Um texto introdutório amigável (2-3 frases) e um resumo da viagem.")
    curated_flights: List[CuratedRecommendation] = PydanticV2Field(description="Lista de 1-2 recomendações de voos.")
    curated_hotels: List[CuratedRecommendation] = PydanticV2Field(description="Lista de 2-3 recomendações de hotéis.")
    curated_activities: List[CuratedRecommendation] = PydanticV2Field(description="Lista de 4-5 recomendações de atividades.")
    closing_text: str = PydanticV2Field(description="Uma frase de encerramento amigável (1-2 frases).")

# --- ESTADO DO GRAFO (ATUALIZADO) ---
class TravelAppState(TypedDict):
    user_request: str
    origin: str | None 
    destination: str | None
    start_date: str | None
    end_date: str | None
    
    # Estes agora guardam os resultados brutos das ferramentas
    raw_flights: List[Dict] | None
    raw_hotels: List[Dict] | None
    raw_activities: List[Dict] | None
    
    # O itinerário em Markdown foi substituído por este objeto
    final_report: FinalReport | None 
    
    error: str | None

# --- Nó de Extração (Atualizado para o novo estado) ---
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
        # Fallback simples (pode não ser necessário se o LLM for robusto)
        return { "error": f"Não foi possível processar a extração. Erro: {e}" }

# --- Nó de Validação de Datas (NOVO) ---
def validate_dates_node(state: TravelAppState) -> dict:
    print("--- ⏱️ Validando as datas ---")
    if state.get("error"):
        return {"error": state.get("error")}
        
    start = state.get("start_date")
    end = state.get("end_date")
    
    if not start or not end:
        return {"error": "As datas de início e fim da viagem não foram encontradas no pedido."}

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
            
        if end_dt < start_dt:
            return {"error": "A data de retorno não pode ser antes da data de partida."}
            
    except ValueError:
        return {"error": "Formato de data inválido. Use AAAA-MM-DD."}
        
    return {} # OK

# --- Agentes de Busca (Atualizados para o novo estado) ---
def flight_agent_node(state: TravelAppState) -> dict:
    print("--- ✈️ Agente de Voos: Chamando ferramenta ---")
    # ... (mesma lógica de verificação de erro) ...
    if state.get("error"):
         return {"raw_flights": [{"id": "error", "error": state.get("error")}]}
         
    try:
        results = search_flights.invoke({
            "origin": state["origin"],
            "destination": state["destination"],
            "departure_date": state["start_date"],
            "return_date": state["end_date"],
            "passengers": 1
        })
        return {"raw_flights": results} # Salva em raw_flights
    except Exception as e:
        print(f"Erro ao chamar ferramenta de voos: {e}")
        return {"raw_flights": [{"id": "error", "error": f"Erro ao buscar voos: {e}"}]}

def hotel_agent_node(state: TravelAppState) -> dict:
    print("--- 🏨 Agente de Hospedagem: Chamando ferramenta ---")
    if state.get("error"):
         return {"raw_hotels": [{"id": "error", "error": state.get("error")}]}

    try:
        results = search_hotels.invoke({
            "destination": state["destination"],
            "check_in_date": state["start_date"],
            "check_out_date": state["end_date"]
        })
        return {"raw_hotels": results} # Salva em raw_hotels
    except Exception as e:
        print(f"Erro ao chamar ferramenta de hotéis: {e}")
        return {"raw_hotels": [{"id": "error", "error": f"Erro ao buscar hotéis: {e}"}]}


def activity_agent_node(state: TravelAppState) -> dict:
    print("--- 🗺️ Agente de Atividades: Chamando ferramenta ---")
    if state.get("error"):
         return {"raw_activities": [{"id": "error", "error": state.get("error")}]}

    try:
        results = search_activities.invoke({
            "destination": state["destination"],
            "start_date": state["start_date"],
            "end_date": state["end_date"]
        })
        return {"raw_activities": results} # Salva em raw_activities
    except Exception as e:
        print(f"Erro ao chamar ferramenta de atividades: {e}")
        return {"raw_activities": [{"id": "error", "error": f"Erro ao buscar atividades: {e}"}]}


# --- NÓ CURADOR (TOTALMENTE REFEITO) ---
def curate_and_report_node(state: TravelAppState) -> dict:
    print("--- 🧠 Agente Curador: Selecionando recomendações e gerando JSON ---")

    initial_error = state.get("error")
    
    # Extrai erros reais das APIs para enviar ao LLM
    def extract_error(results: List[Dict] | None) -> str | None:
        if results:
            for item in results:
                if item.get("id") == "error":
                    return item.get("airline") or item.get("error") or str(item)
        return None
        
    def filter_valid(results: List[Dict] | None) -> List[Dict]:
        if not results:
            return []
        return [item for item in results if item.get("id") != "error"]

    found_flights = filter_valid(state.get("raw_flights"))
    found_hotels = filter_valid(state.get("raw_hotels"))
    found_activities = filter_valid(state.get("raw_activities"))
    
    flights_error = extract_error(state.get("raw_flights"))
    hotels_error = extract_error(state.get("raw_hotels"))
    activities_error = extract_error(state.get("raw_activities"))

    # Converte os resultados limpos para JSON para enviar ao LLM
    flights_json = json.dumps(found_flights, indent=2, ensure_ascii=False)
    hotels_json = json.dumps(found_hotels, indent=2, ensure_ascii=False)
    activities_json = json.dumps(found_activities, indent=2, ensure_ascii=False)

    # Se houver um erro de extração e NENHUMA ferramenta retornou dados, encerra
    if initial_error and not found_flights and not found_hotels and not found_activities:
         print(f"Retornando erro inicial: {initial_error}")
         return {
            "final_report": None,
            "error": initial_error
         }

    # Define o parser de saída para o nosso novo modelo FinalReport
    parser = PydanticOutputParser(pydantic_object=FinalReport)

    summary_prompt = f"""
    Você é um agente de viagens especialista e seu trabalho é criar um "Relatório de Recomendações"
    para um usuário. Você recebeu dados brutos de ferramentas de busca e agora deve analisá-los,
    selecionar as melhores opções e justificar suas escolhas.

    O pedido original do usuário foi:
    "{state['user_request']}"

    Informações da Viagem:
    Destino: {state.get('destination', 'Não extraído')}
    Período: {state.get('start_date', 'Não extraído')} a {state.get('end_date', 'Não extraído')}

    --- DADOS BRUTOS DAS FERRAMENTAS ---
    Voos: {flights_json}
    Hotéis: {hotels_json}
    Atividades: {activities_json}

    --- ERROS REPORTADOS PELAS APIS (Informativo para o relatório) ---
    Se houver erros abaixo, não inclua esse item, mas avise o usuário de forma amigável no sumário (e.g. "Não encontramos voos por X, mas veja hotéis!").
    Erro Voos: {flights_error or 'Nenhum'}
    Erro Hotéis: {hotels_error or 'Nenhum'}
    Erro Atividades: {activities_error or 'Nenhum'}

    --- CÁLCULO DE DIAS ---
    Início: {state.get('start_date', 'Não extraído')}
    Fim: {state.get('end_date', 'Não extraído')}

    --- SUA TAREFA ---
    Analise as listas JSON fornecidas. Selecione as MELHORES opções de Viagem:
    1. Voos: Escolha 1-2 voos.
    2. Hotéis: Escolha 2-3 hotéis.
    3. Atividades: Escolha exatamente **UMA ATIVIDADE DIFERENTE PARA CADA DIA DA VIAGEM** (calcule os dias entre {state.get('start_date')} e {state.get('end_date')}). Nas justificativas das atividades, inicie com "Dia X:" (ex: "Dia 1: Incrível para iniciar a viagem..."). Dê preferência a atrações do local exato, mas se acabarem as opções, sugira na região vizinha próxima!
    
    Se uma lista estiver vazia, retorne uma lista vazia para ela (ex: "curated_flights": []).
    
    Gere um objeto JSON que siga estritamente o formato abaixo.
    {parser.get_format_instructions()}
    """

    print("--- 🤖 Gerando relatório JSON curado com o Gemini... ---")

    chain = llm | parser

    try:
        report: FinalReport = chain.invoke(summary_prompt)
        
        # Retorna o objeto Pydantic
        return {
            "final_report": report,
            "error": initial_error # Mantém o erro inicial se houver, mas o relatório foi gerado
        }
    except Exception as e:
        print(f"!!! Erro crítico ao gerar relatório JSON curado: {e}")
        return {
            "final_report": None,
            "error": f"Erro do Agente Curador: {e}"
        }


# --- Definição do Grafo (ATUALIZADO) ---
print("Construindo o gráfico de agentes LangGraph...")
workflow = StateGraph(TravelAppState)
workflow.add_node("extract_info", extract_info_node)
workflow.add_node("validate_dates", validate_dates_node)
workflow.add_node("flights", flight_agent_node)
workflow.add_node("hotels", hotel_agent_node)
workflow.add_node("activities", activity_agent_node)
workflow.add_node("curate_and_report", curate_and_report_node) 

workflow.set_entry_point("extract_info")
workflow.add_edge("extract_info", "validate_dates")

# Execução Paralela!
workflow.add_edge("validate_dates", "flights")
workflow.add_edge("validate_dates", "hotels")
workflow.add_edge("validate_dates", "activities")

workflow.add_edge("flights", "curate_and_report")
workflow.add_edge("hotels", "curate_and_report")
workflow.add_edge("activities", "curate_and_report")
workflow.add_edge("curate_and_report", END)

app = workflow.compile()
print("Gráfico compilado com sucesso.")

# --- Execução __main__ (para teste) ---
if __name__ == "__main__":
    print("\n--- Iniciando Planejamento da Viagem (Execução Direta) ---")
    user_input = "Planeje uma viagem de São Paulo para Curitiba de 2025-12-10 até 2025-12-17"
    
    # Estado inicial atualizado
    initial_state = TravelAppState( 
        user_request= user_input, 
        origin=None, destination= None, 
        start_date= None, end_date= None, 
        raw_flights= None, raw_hotels= None, raw_activities= None, 
        final_report= None, 
        error= None 
    )
    
    try:
        final_response_state = app.invoke(initial_state)
        print("\n--- Planejamento Concluído! ---")
        print("\n" + "="*50)
        print("             RELATÓRIO FINAL GERADO (JSON)")
        print("="*50 + "\n")
        
        if final_response_state.get('final_report'):
            # Converte o objeto Pydantic para um dict para impressão bonita
            report_dict = final_response_state['final_report'].dict()
            print(json.dumps(report_dict, indent=2, ensure_ascii=False))
        else:
            print("Nenhum relatório gerado.")
            
        print("\nErro:", final_response_state.get('error'))
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"\nErro durante a execução do gráfico: {e}")
        import traceback
        traceback.print_exc()
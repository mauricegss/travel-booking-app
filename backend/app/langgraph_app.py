import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import operator

# Importações específicas do LangChain e Google GenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# Importa as funções mock das ferramentas (embora não sejam usadas diretamente neste exemplo inicial)
from app.tools.flight_tools import search_flights
from app.tools.hotel_tools import search_hotels
from app.tools.activity_tools import search_activities
from app.tools.booking_tools import confirm_booking, process_payment

# --- Configuração Inicial ---

# Carrega as variáveis de ambiente (especialmente a GOOGLE_API_KEY do arquivo .env no diretório backend)
# __file__ se refere a este arquivo (langgraph_app.py)
# os.path.dirname obtém o diretório (backend/app)
# os.path.join monta o caminho para o diretório backend
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Verifica se a chave da API do Google está configurada
if 'GOOGLE_API_KEY' not in os.environ:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
    print(f"Por favor, crie um arquivo .env no diretório '{os.path.dirname(dotenv_path)}' e adicione sua chave.")
    exit()
else:
    print("GOOGLE_API_KEY carregada com sucesso.")


# Inicializa o modelo LLM (Gemini 1.5 Pro)
# Usamos uma temperatura baixa (0.2) para respostas mais consistentes
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.2)
    print("Modelo ChatGoogleGenerativeAI inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o ChatGoogleGenerativeAI: {e}")
    print("Verifique sua GOOGLE_API_KEY e a instalação das bibliotecas.")
    exit()

# --- Definição do Estado do Grafo ---

# O "Estado" é o objeto central que todos os agentes irão ler e modificar.
class TravelAppState(TypedDict):
    user_request: str  # O pedido original do usuário
    destination: str | None # Destino extraído (pode ser adicionado por um nó futuro)
    start_date: str | None # Data de início extraída
    end_date: str | None   # Data de fim extraída
    flights: str       # A resposta do agente de voos
    hotels: str        # A resposta do agente de hospedagem
    activities: str    # A resposta do agente de atividades
    itinerary: str     # O itinerário final consolidado

# --- Definição dos Agentes (Nós do Grafo) ---

# Cada agente é uma função (um "nó" no grafo) que recebe o estado atual,
# executa sua lógica (simulada pelo LLM aqui) e retorna um dicionário
# para atualizar o estado.

def flight_agent_node(state: TravelAppState) -> dict:
    """
    Agente simulado para encontrar voos.
    """
    print("--- ✈️ Agente de Voos: Buscando opções ---")
    user_request = state['user_request']

    system_prompt = """
    Você é um agente de viagens especialista em encontrar voos. Sua tarefa é encontrar
    as 2-3 melhores opções de voos (ida e volta) para o pedido do usuário.
    Seja conciso, mas inclua companhia aérea (fictícia), horários aproximados e preço médio.
    Responda APENAS com as opções de voos. Extraia o destino principal do pedido do usuário.
    Formato esperado da resposta (exemplo):
    Destino Principal: Paris
    Opções de Voos:
    - Opção 1...
    - Opção 2...
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_request)
    ]

    response = llm.invoke(messages)
    # TODO: Extrair o 'Destino Principal' da resposta e atualizar state['destination']
    return {"flights": response.content}

def hotel_agent_node(state: TravelAppState) -> dict:
    """
    Agente simulado para encontrar hospedagem.
    """
    print("--- 🏨 Agente de Hospedagem: Pesquisando hotéis ---")
    user_request = state['user_request']
    # Idealmente, usaria state['destination'], state['start_date'], state['end_date'] se extraídos

    system_prompt = """
    Você é um agente de viagens especialista em hospedagem com base no destino.
    Sua tarefa é sugerir 3 opções de hotéis que se encaixem no pedido do usuário,
    cobrindo diferentes faixas de preço (Luxo, Conforto, Econômico).
    Inclua o nome do hotel (fictício), uma breve descrição e preço médio por noite.
    Responda APENAS com as opções de hotéis.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_request) # Poderia passar infos mais específicas do estado
    ]

    response = llm.invoke(messages)
    return {"hotels": response.content}

def activity_agent_node(state: TravelAppState) -> dict:
    """
    Agente simulado para sugerir atividades locais.
    """
    print("--- 🗺️ Agente de Atividades: Sugerindo passeios ---")
    user_request = state['user_request']
    # Idealmente, usaria state['destination']

    system_prompt = """
    Você é um guia turístico local entusiasmado e experiente no destino do usuário.
    Sua tarefa é recomendar 5 atividades ou atrações imperdíveis.
    Inclua uma mistura de pontos turísticos famosos e "joias escondidas".
    Responda APENAS com a lista de atividades.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_request) # Poderia passar infos mais específicas do estado
    ]

    response = llm.invoke(messages)
    return {"activities": response.content}

def integration_agent_node(state: TravelAppState) -> dict:
    """
    Agente final simulado que consolida todas as informações em um itinerário.
    """
    print("--- 🧾 Agente de Integração: Montando o itinerário final ---")

    summary_prompt = f"""
    Você é o agente de integração mestre. Sua tarefa é pegar as informações
    coletadas pelos outros agentes e apresentá-las ao usuário de forma clara,
    organizada e amigável, como um plano de viagem completo.

    O pedido original do usuário foi:
    {state['user_request']}

    Informações de Voos:
    {state['flights']}

    Informações de Hospedagem:
    {state['hotels']}

    Sugestões de Atividades:
    {state['activities']}

    Compile tudo isso em um único itinerário. Adicione uma saudação amigável
    e uma frase de encerramento (ex: "Qualquer alteração, basta me avisar!").
    Certifique-se de apresentar um plano coeso e lógico.
    """

    print("--- 🤖 Processando o itinerário completo... (Isso pode levar um momento) ---")

    messages = [
        SystemMessage(content="Você é um agente de viagens sênior montando um plano final."),
        HumanMessage(content=summary_prompt)
    ]

    response = llm.invoke(messages)
    return {"itinerary": response.content}

# --- Construção do Grafo (Workflow) ---

print("Construindo o gráfico de agentes LangGraph...")
workflow = StateGraph(TravelAppState)

# Adicionar os nós
workflow.add_node("flights", flight_agent_node)
workflow.add_node("hotels", hotel_agent_node)
workflow.add_node("activities", activity_agent_node)
workflow.add_node("integrator", integration_agent_node)

# Definir as arestas (fluxo sequencial simples neste exemplo)
workflow.set_entry_point("flights")
workflow.add_edge("flights", "hotels")
workflow.add_edge("hotels", "activities")
workflow.add_edge("activities", "integrator")
workflow.add_edge("integrator", END)

# Compilar o gráfico
app = workflow.compile()
print("Gráfico compilado com sucesso.")

# --- Execução Principal (se o script for rodado diretamente) ---

if __name__ == "__main__":
    print("\n--- Iniciando Planejamento da Viagem (Execução Direta) ---")

    # Exemplo de input
    user_input = "Planeje uma viagem de São Paulo a Tóquio, 7 dias em abril."

    initial_state = {
        "user_request": user_input,
        "destination": None,
        "start_date": None,
        "end_date": None,
        "flights": "", # Inicializa strings vazias para evitar erros
        "hotels": "",
        "activities": "",
        "itinerary": ""
        }

    # Invocar o gráfico
    try:
        final_response_state = app.invoke(initial_state)

        print("\n--- Planejamento Concluído! ---")

        # Exibir o resultado final
        print("\n" + "="*50)
        print("             ITINERÁRIO FINAL GERADO")
        print("="*50 + "\n")
        print(final_response_state.get('itinerary', "Nenhum itinerário gerado.")) # Usar .get para segurança
        print("\n" + "="*50 + "\n")

    except Exception as e:
        print(f"\nErro durante a execução do gráfico: {e}")
        import traceback
        traceback.print_exc()
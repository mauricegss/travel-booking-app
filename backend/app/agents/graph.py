# backend/app/agents/graph.py
from google import adk
import os
from dotenv import load_dotenv
# Importamos os outros agentes para que o integration_agent possa, teoricamente, chamá-los se necessário no futuro,
# ou para que possamos exportá-los todos juntos a partir daqui, se quisermos.
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.activity_agent import activity_agent

load_dotenv()

# adk.init() # Descomente se precisar inicializar explicitamente

# Definimos apenas o Agente de Integração aqui
integration_agent = adk.Agent(
    name="BookingIntegrator",
    description="Coordena os agentes de voos, hotéis e atividades, consolida as informações e lida com a confirmação da reserva e pagamento.",
    # model="gemini-2.5-flash", # Ou o modelo desejado
    # tools=[] # Ferramentas para pagamento/confirmação serão adicionadas aqui
)

# Não precisamos mais do AgentGraph aqui, ele será removido.
# A orquestração será feita no endpoint da API (Etapa 3).

# O bloco de teste abaixo pode ser removido ou adaptado para testar apenas o integration_agent, se desejar.
if __name__ == "__main__":
    print("Testando inicialização do Integration Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        # Apenas verificamos se o objeto foi criado
        if integration_agent:
             print("Inicialização básica do integration_agent parece OK.")
        else:
             print("Falha ao inicializar integration_agent.")

    except Exception as e:
        print(f"Erro durante o teste do agente de integração: {e}")
        import traceback
        traceback.print_exc()
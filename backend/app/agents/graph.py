from google import adk
import os
from dotenv import load_dotenv
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.activity_agent import activity_agent
from app.tools.booking_tools import confirm_booking, process_payment

load_dotenv()

integration_agent = adk.Agent(
    name="BookingIntegrator",
    description="Coordena os agentes de voos, hotéis e atividades, consolida as informações e lida com a confirmação da reserva e pagamento.",
    model="gemini-2.5-flash", # Modelo explicitamente definido
    tools=[confirm_booking, process_payment]
)

if __name__ == "__main__":
    print("Testando inicialização do Integration Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        if integration_agent:
             print("Inicialização básica do integration_agent parece OK.")
        else:
             print("Falha ao inicializar integration_agent.")

    except Exception as e:
        print(f"Erro durante o teste do agente de integração: {e}")
        import traceback
        traceback.print_exc()
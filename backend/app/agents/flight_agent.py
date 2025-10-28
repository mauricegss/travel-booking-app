from google import adk
import os
from dotenv import load_dotenv
from app.tools.flight_tools import search_flights

load_dotenv()

flight_agent = adk.Agent(
    name="FlightFinder",
    description="Busca as melhores opções de voos com base nas preferências do usuário, como origem, destino, datas e orçamento.",
    model="gemini-2.5-flash", # Modelo explicitamente definido
    tools=[search_flights]
)

if __name__ == "__main__":
    print("Testando FlightFinder Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        prompt = "Encontre voos de Curitiba para Paris para 5 dias em novembro."
        print(f"Executando com o prompt: '{prompt}'")

        print("Inicialização básica do agente parece OK.")
    except Exception as e:
        print(f"Erro durante o teste do agente: {e}")
        import traceback
        traceback.print_exc()
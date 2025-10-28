from google import adk
import os
from dotenv import load_dotenv
from app.tools.activity_tools import search_activities

load_dotenv()

activity_agent = adk.Agent(
    name="ActivityFinder",
    description="Recomenda atividades locais, atrações turísticas e eventos com base nos interesses do usuário e no destino da viagem.",
    model="gemini-2.5-flash", # Modelo explicitamente definido
    tools=[search_activities]
)

if __name__ == "__main__":
    print("Testando ActivityFinder Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        prompt = "Quais atividades e passeios são imperdíveis em Paris para uma viagem em novembro?"
        print(f"Executando com o prompt: '{prompt}'")

        print("Inicialização básica do agente parece OK.")
    except Exception as e:
        print(f"Erro durante o teste do agente: {e}")
        import traceback
        traceback.print_exc()
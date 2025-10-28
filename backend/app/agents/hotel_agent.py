from google import adk
import os
from dotenv import load_dotenv
from app.tools.hotel_tools import search_hotels

load_dotenv()

hotel_agent = adk.Agent(
    name="HotelRecommender",
    description="Recomenda hotéis com base no destino, datas, orçamento, localização preferida e serviços desejados pelo usuário.",
    model="gemini-2.5-flash", # Modelo explicitamente definido
    tools=[search_hotels]
)

if __name__ == "__main__":
    print("Testando HotelRecommender Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        prompt = "Sugira hotéis em Paris para 5 dias em novembro, com bom custo-benefício e perto de atrações turísticas."
        print(f"Executando com o prompt: '{prompt}'")

        print("Inicialização básica do agente parece OK.")
    except Exception as e:
        print(f"Erro durante o teste do agente: {e}")
        import traceback
        traceback.print_exc()
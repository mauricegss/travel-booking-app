# backend/app/agents/hotel_agent.py
from google import adk
import os
from dotenv import load_dotenv # Importe a função

load_dotenv() # Chame a função aqui no início

# adk.init() # Descomente se precisar inicializar explicitamente

hotel_agent = adk.Agent(
    name="HotelRecommender",
    description="Recomenda hotéis com base no destino, datas, orçamento, localização preferida e serviços desejados pelo usuário.",
    # model="gemini-2.5-flash", # Ou o modelo desejado
    # tools=[] # Ferramentas para APIs de hotéis serão adicionadas aqui
)

# Exemplo de como você poderia testar o agente (opcional neste arquivo)
if __name__ == "__main__":
    print("Testando HotelRecommender Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        prompt = "Sugira hotéis em Paris para 5 dias em novembro, com bom custo-benefício e perto de atrações turísticas."
        print(f"Executando com o prompt: '{prompt}'")
        # response = hotel_agent.run(prompt) # Mantenha comentado por enquanto
        # print("Resposta do agente:") # Mantenha comentado por enquanto
        # print(response) # Mantenha comentado por enquanto
        print("Inicialização básica do agente parece OK (sem chamada run).")
    except Exception as e:
        print(f"Erro durante o teste do agente: {e}")
        import traceback
        traceback.print_exc()
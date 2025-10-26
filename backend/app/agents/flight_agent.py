# backend/app/agents/flight_agent.py
from google import adk
import os
from dotenv import load_dotenv # Importe a função

load_dotenv() # Chame a função aqui no início

# adk.init() # Descomente se precisar inicializar explicitamente

flight_agent = adk.Agent(
    name="FlightFinder",
    description="Busca as melhores opções de voos com base nas preferências do usuário, como origem, destino, datas e orçamento.",
    # model="gemini-2.5-flash", # Ou o modelo desejado
    # tools=[] # Ferramentas para APIs de voos serão adicionadas aqui
)

if __name__ == "__main__":
    print("Testando FlightFinder Agent...")
    try:
        # Agora o os.getenv deve encontrar a variável carregada pelo load_dotenv()
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        prompt = "Encontre voos de Curitiba para Paris para 5 dias em novembro."
        print(f"Executando com o prompt: '{prompt}'")
        # response = flight_agent.run(prompt) # Mantenha comentado por enquanto
        # print("Resposta do agente:") # Mantenha comentado por enquanto
        # print(response) # Mantenha comentado por enquanto
        print("Inicialização básica do agente parece OK (sem chamada run).")
    except Exception as e:
        print(f"Erro durante o teste do agente: {e}")
        import traceback
        traceback.print_exc()
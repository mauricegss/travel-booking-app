# backend/app/agents/activity_agent.py
from google import adk
import os
from dotenv import load_dotenv # Importe a função

load_dotenv() # Chame a função aqui no início

# adk.init() # Descomente se precisar inicializar explicitamente

activity_agent = adk.Agent(
    name="ActivityFinder",
    description="Recomenda atividades locais, atrações turísticas e eventos com base nos interesses do usuário e no destino da viagem.",
    # model="gemini-2.5-flash", # Ou o modelo desejado
    # tools=[] # Ferramentas para APIs de atividades/eventos serão adicionadas aqui
)

# Exemplo de como você poderia testar o agente (opcional neste arquivo)
if __name__ == "__main__":
    print("Testando ActivityFinder Agent...")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            print("AVISO: Variável de ambiente GOOGLE_API_KEY não definida.")
        else:
            print("GOOGLE_API_KEY carregada com sucesso do .env")

        prompt = "Quais atividades e passeios são imperdíveis em Paris para uma viagem em novembro?"
        print(f"Executando com o prompt: '{prompt}'")
        # response = activity_agent.run(prompt) # Mantenha comentado por enquanto
        # print("Resposta do agente:") # Mantenha comentado por enquanto
        # print(response) # Mantenha comentado por enquanto
        print("Inicialização básica do agente parece OK (sem chamada run).")
    except Exception as e:
        print(f"Erro durante o teste do agente: {e}")
        import traceback
        traceback.print_exc()
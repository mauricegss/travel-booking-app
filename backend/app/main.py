from fastapi import FastAPI
from dotenv import load_dotenv
import os
# from app.api.endpoints import router as api_router
# app.include_router(api_router, prefix="/api")

# Carrega variáveis de ambiente do arquivo .env (opcional, mas útil para chaves de API)
load_dotenv()

# Crie a instância do FastAPI
app = FastAPI(title="Travel Booking AI Agent API")

# Exemplo de endpoint raiz
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API do Travel Booking App com Agentes de IA"}

# Você adicionará mais endpoints aqui, como os de busca e reserva
# Exemplo futuro: app.include_router(api_router, prefix="/api")

# Se você for rodar diretamente com 'python main.py' (não recomendado para produção)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
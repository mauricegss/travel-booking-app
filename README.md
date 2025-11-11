# Travel Booking App - Agente de Viagens com IA

Este é um aplicativo full-stack de planejamento de viagens que utiliza um sistema de agentes de IA, construído com **LangGraph** e o modelo **Gemini** do Google, para pesquisar e montar um roteiro de viagem coeso.

O frontend é uma interface moderna construída com **React**, **Vite**, **TypeScript** e **shadcn-ui**. O backend é um servidor **FastAPI** em Python que orquestra os agentes de IA.

## 🤖 Conceito: Como Funciona

O diferencial deste projeto é o **Agente Curador** no backend. Em vez de simplesmente despejar os resultados da API no frontend, o sistema segue um fluxo inteligente:

1.  **Frontend (React):** O usuário insere a Origem, Destino e Datas na `SearchBar`.
2.  **Backend (FastAPI):** O frontend envia uma *única string* de linguagem natural (ex: "Planeje uma viagem de São Paulo para Curitiba...") para o endpoint `/plan-trip`.
3.  **Backend (LangGraph):** O servidor FastAPI aciona um grafo LangGraph (`app.py`) que orquestra vários agentes:
    * **Agente Extrator:** Um LLM (Gemini) primeiro extrai as entidades estruturadas (origem, destino, datas) da string.
    * **Agentes de Ferramentas:** O grafo chama as ferramentas de busca com os dados extraídos:
        * `search_flights`: Busca voos usando **AviationStack** e **Tavily** (para códigos IATA).
        * `Google Hotels`: Busca hotéis usando **Geoapify**.
        * `search_activities`: Busca atividades e pontos turísticos usando **Geoapify**.
    * **Agente Curador (O Cérebro):** Um nó final do LangGraph (`curate_and_report_node`) recebe *todos* os dados brutos em JSON das ferramentas. Ele então usa o Gemini com um prompt detalhado para atuar como um "agente de viagens especialista", selecionando as **melhores 1-2 opções de voos**, **3 hotéis** e **4-5 atividades**, escrevendo um relatório coeso e justificado em Markdown.
4.  **Resultado (React):** O frontend recebe o relatório final em Markdown e os dados filtrados, exibindo-os na página de resultados (`SearchResults.tsx`).

## 🛠️ Tecnologias Utilizadas

| Área | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Frontend** | React | Biblioteca principal da UI. |
| | Vite | Build tool e servidor de desenvolvimento. |
| | TypeScript | Tipagem estática. |
| | Tailwind CSS | Estilização CSS. |
| | shadcn-ui | Componentes de UI (Cards, Botões, etc.). |
| | React Router | Roteamento de páginas (`/` e `/search-results`). |
| **Backend** | Python | Linguagem principal. |
| | FastAPI | Servidor web ASGI para a API. |
| | LangGraph | Orquestração do fluxo de agentes (StateGraph). |
| | LangChain | Integrações (`langchain-google-genai`). |
| | Google Gemini | Modelo de LLM para extração e curadoria. |
| **APIs** | Tavily | Busca web (usada para encontrar códigos IATA). |
| | AviationStack | API de dados de voos (horários). |
| | Geoapify | API de geocodificação e busca de locais (Hotéis, Atividades). |

## 🚀 Configuração e Execução

### 1. Pré-requisitos

* Node.js (v18+) e npm
* Python (v3.10+) e pip
* Chaves de API para:
    * Google (Gemini)
    * Tavily
    * AviationStack
    * Geoapify

### 2. Backend (FastAPI + LangGraph)

Primeiro, configure e inicie o servidor de backend.

```bash
# 1. Navegue até a pasta do backend
cd backend

# 2. Crie um ambiente virtual e ative-o
python -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione suas chaves de API
# GOOGLE_API_KEY=...
# TAVILY_API_KEY=...
# AVIATIONSTACK_API_KEY=...
# GEOAPIFY_API_KEY=...

# 5. Inicie o servidor FastAPI
# O frontend espera que ele rode na porta 8000
uvicorn app.main:api --host 127.0.0.1 --port 8000 --reload

### 3. Frontend (React + Vite)

Em um novo terminal, configure e inicie o frontend.

# 1. Volte para o diretório raiz (se estiver em /backend)
cd ..

# 2. Instale as dependências do Node.js
npm install

# 3. Inicie o servidor de desenvolvimento do Vite
npm run dev
Abra seu navegador em http://localhost:8080 (ou qualquer porta que o Vite indicar) para ver o aplicativo em execução.
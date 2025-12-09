# Como Instalar e Usar o Travel Booking App

Bem-vindo ao guia de iniciação do **Travel Booking App**. Este tutorial foi desenhado para te ajudar a configurar e explorar o nosso agente de viagens inteligente de forma rápida e simples.

## 1. Introdução

### O que é o Travel Booking App?
O Travel Booking App é uma aplicação *full-stack* de planejamento de viagens que utiliza um sistema de agentes de IA, construído com **LangGraph** e o modelo **Gemini** do Google.

Imagine-o como uma **"Agência de Viagens Digital"** completa. Diferente de sites de busca comuns, este sistema possui um **Agente Curador** que não apenas pesquisa, mas seleciona e justifica as melhores opções para ti, criando um roteiro coeso com imagens reais dos locais.

### Para que serve?
Podes conversar com ele para:
* **Planejar roteiros complexos:** Definir voos, hotéis e atividades com uma única frase em linguagem natural.
* **Busca em Tempo Real:** O sistema consulta dados reais de preços e horários usando o Google Flights e Google Hotels (via SerpAPI).
* **Obter recomendações visuais:** O relatório final inclui fotos dos hotéis, companhias aéreas e atrações turísticas.

## 2. Pré-requisitos

Antes de começarmos, garante que tens as seguintes ferramentas instaladas no teu computador:

* **Node.js** (v18 ou superior) & **npm** (para o Frontend).
* **Python** (v3.10 ou superior) & **pip** (para o Backend).
* **Chaves de API** (necessárias para os serviços de busca). Precisarás das seguintes:
    * **Google API Key** (para o cérebro do modelo Gemini).
    * **Tavily API Key** (para descobrir códigos de aeroportos IATA).
    * **SerpAPI Key** (para buscar dados reais de Voos e Hotéis no Google).
    * **Geoapify API Key** (para buscar Atividades e Atrações Turísticas).

## 3. Instalação Rápida

O sistema está dividido em duas partes: o **Backend** (API Python com LangGraph) e o **Frontend** (Interface React). Vamos configurar ambos.

### Passo A: Configurar o Backend (API)

1.  Abre o teu terminal e entra na pasta do backend:
    ```bash
    cd backend
    ```

2.  Cria um ambiente virtual para isolar as dependências (recomendado):
    ```bash
    python -m venv venv
    # No Windows, ativa com: .\venv\Scripts\activate
    # No Linux/Mac, ativa com: source venv/bin/activate
    ```

3.  Instala as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura as tuas Chaves de API:**
    Cria um ficheiro chamado `.env` dentro da pasta `backend` e preenche com as chaves corretas:

    **Exemplo (.env)**
    ```ini
    GOOGLE_API_KEY="SUA_CHAVE_AQUI"
    TAVILY_API_KEY="SUA_CHAVE_AQUI"
    SERPAPI_API_KEY="SUA_CHAVE_AQUI"
    GEOAPIFY_API_KEY="SUA_CHAVE_AQUI"
    ```

### Passo B: Configurar o Frontend (Interface)

1.  Abre um novo terminal e volta à raiz do projeto (se estiveres na pasta `backend`, recua uma vez):
    ```bash
    cd ..
    ```

2.  Instala as dependências da interface visual:
    ```bash
    npm install
    ```

## 4. Como Usar

Agora vamos colocar tudo a funcionar!

### 1. Iniciar o Servidor (Backend):
No terminal do Backend (com o ambiente virtual ativo), inicia o servidor FastAPI.

```bash
uvicorn app.main:api --host 127.0.0.1 --port 8000 --reload

```

### 2. Iniciar a Interface (Frontend):

No terminal do Frontend, executa o servidor de desenvolvimento:

Bash

```
npm run dev

```

O terminal irá mostrar um endereço local, geralmente `http://localhost:8080`.

### 3. Interagir:

-   Abre o teu navegador e vai ao endereço indicado.
    
-   Na barra de pesquisa, experimenta fazer um pedido completo:
    
    > _"Planeje uma viagem de Lisboa para Paris de 15/09/2025 a 20/09/2025"_
    

O sistema irá processar o pedido, buscar voos e hotéis no Google, atividades locais e exibir um relatório detalhado com fotos.

----------

**Dica Pro:** O Travel Booking App segue um fluxo de pensamento inteligente (**LangGraph**):

1.  **Extração:** Identifica datas e locais.
    
2.  **Ferramentas:**
    
    -   Usa **Tavily** para achar o código IATA (ex: "LIS" para Lisboa).
        
    -   Usa **SerpAPI** para varrer o Google Flights e Google Hotels.
        
    -   Usa **Geoapify** para encontrar parques e museus próximos.
        
3.  **Curadoria:** O Gemini lê os JSONs brutos, escolhe as melhores opções (baseado em preço e avaliação) e gera o relatório final.
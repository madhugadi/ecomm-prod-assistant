# 🛒 E-Commerce Product Assistant

An AI shopping assistant that answers natural-language questions about products, such as *"Which iPhone 15 model has the best battery reviews?"*, using real product data and customer reviews.

It's built as an **agentic RAG** system. A LangGraph agent decides whether to search the product database or the live web, checks whether what it found is actually relevant, rewrites the question if it isn't, and only then writes an answer.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?logo=langchain&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6E56CF)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Kubernetes](https://img.shields.io/badge/AWS-EKS-FF9900?logo=amazonaws&logoColor=white)

---

## ✨ Features

- **Product review scraping:** a Streamlit tool collects product titles, ratings, prices, and top reviews
- **Vector search on Astra DB:** reviews are embedded and stored for semantic search
- **Smarter retrieval:** MMR search for diverse results, plus an LLM filter that drops irrelevant chunks before they reach the model (fewer tokens, fewer hallucinations)
- **Agentic workflow:** the agent grades retrieved documents and rewrites the query when results are weak
- **Web search fallback:** if the product database can't answer, it searches the web with DuckDuckGo for up-to-date info
- **MCP tool server:** retrieval and web search are exposed as tools through the Model Context Protocol, keeping each piece modular
- **RAGAS evaluation:** measures answer quality and context precision
- **Production deployment:** Docker, Kubernetes on **AWS EKS**, CI/CD with GitHub Actions

---

## 🏗️ How It Works

```
                    ┌─────────────┐
 User question ───► │  Assistant  │  decides: product DB or web?
                    └──────┬──────┘
               ┌───────────┴───────────┐
               ▼                       ▼
        ┌────────────┐          ┌────────────┐
        │ Retriever  │          │ Web Search │   ◄── both are MCP tools
        │ (Astra DB) │          │(DuckDuckGo)│
        └─────┬──────┘          └─────┬──────┘
              ▼                       │
      Grade documents                 │
       ├── relevant ──► Generator ◄───┘ ──► Answer
       └── weak ──────► Rewriter ──► retry
```

---

## 🧰 Tech Stack

**AI:** LangChain · LangGraph · MCP · Astra DB (vector store) · Groq · Google Gemini · RAGAS
**App:** Python 3.11 · FastAPI · Jinja2 templates · Streamlit (scraper UI)
**DevOps:** Docker · Kubernetes · AWS EKS · Amazon ECR · CloudFormation · GitHub Actions · uv

---

## 📁 Project Structure

```
ecomm-prod-assistant/
├── prod_assistant/
│   ├── router/main.py         # FastAPI app (chat endpoint + web UI)
│   ├── workflow/              # LangGraph agent workflows
│   ├── mcp_servers/           # MCP server: product search + web search tools
│   ├── retriever/             # Astra DB retriever with MMR + compression
│   ├── etl/                   # Review scraper and data ingestion
│   ├── evaluation/            # RAGAS evaluation
│   ├── prompt_library/        # Prompt templates
│   └── utils/ · logger/ · exception/
├── scrapper_ui.py             # Streamlit UI for collecting product data
├── data/                      # Sample product reviews
├── templates/ · static/       # Chat web interface
├── infra/                     # CloudFormation: EKS cluster + ECR
├── k8/                        # Kubernetes deployment and service
├── .github/workflows/         # Infrastructure and deploy pipelines
└── Dockerfile
```

---

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/madhugadi/ecomm-prod-assistant.git
cd ecomm-prod-assistant

uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Add your keys

Create a `.env` file in the project root:

```env
LLM_PROVIDER=groq              # or "google"
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key

ASTRA_DB_API_ENDPOINT=your_astra_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astra_token
ASTRA_DB_KEYSPACE=your_keyspace
```

### 3. Load product data (optional)

```bash
streamlit run scrapper_ui.py
```

Enter product names to scrape and ingest them into Astra DB. A sample dataset is included in `data/product_reviews.csv`.

### 4. Start the assistant

```bash
# Start the MCP tool server
python prod_assistant/mcp_servers/product_search_server.py &

# Start the API
uvicorn prod_assistant.router.main:app --reload --port 8000
```

Open **http://localhost:8000** and start asking about products.

### Run with Docker

```bash
docker build -t ecomm-assistant .
docker run -p 8000:8000 --env-file .env ecomm-assistant
```

---

## ☁️ Deployment

1. `infra/eks-with-ecr.yaml` creates the EKS cluster and ECR repository using CloudFormation
2. GitHub Actions builds the Docker image and pushes it to ECR
3. The app is rolled out to EKS using the manifests in `k8/`
4. Logs and metrics go to CloudWatch

---

## 👤 Author

**Madhu** · [GitHub](https://github.com/madhugadi)

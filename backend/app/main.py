import duckdb
import requests
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager

# Importações internas
from app.services.llm import infer_schema_from_sample
from app.database import init_db

# 1. Configuração do Lifespan (Inicialização do Banco)
# Isso garante que o PostGIS e os Schemas sejam criados ao iniciar a API
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa na inicialização
    await init_db()
    yield
    # Executaria no desligamento (se necessário)

# 2. Definição da App com Lifespan
app = FastAPI(
    title="EasyAPIGIS Middleware",
    description="Smart API Gateway for Geospatial Data Inference",
    version="0.1.0",
    lifespan=lifespan
)

# 3. Configuração do CORS (CRÍTICO PARA O FRONTEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que o Frontend (porta 5173) acesse
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    duckdb_version: str
    message: str

@app.get("/", response_model=HealthResponse)
def health_check():
    """
    Verifica se a API está rodando e se o DuckDB está respondendo.
    """
    try:
        conn = duckdb.connect(database=':memory:')
        version = conn.execute("SELECT version()").fetchone()[0]
        return {
            "status": "online",
            "duckdb_version": version,
            "message": "System is ready to crunch spatial data."
        }
    except Exception as e:
        return {
            "status": "error",
            "duckdb_version": "unknown",
            "message": str(e)
        }

# 4. Novo Endpoint Proxy (CRÍTICO PARA BAIXAR DADOS)
# Atualize o endpoint /fetch
@app.get("/fetch")
def fetch_external_url(
    url: str, 
    # Aceita um header opcional chamado 'x-proxy-auth'
    x_proxy_auth: str | None = Header(default=None) 
):
    """
    Baixa o JSON de uma URL externa.
    Se o header 'x-proxy-auth' for enviado, ele é repassado como 'Authorization'.
    """
    try:
        # Prepara os headers para a API de destino
        target_headers = {}
        if x_proxy_auth:
            target_headers['Authorization'] = x_proxy_auth
        
        # Faz a requisição repassando os headers
        # Adicionei um User-Agent genérico pois algumas APIs bloqueiam requests sem ele
        target_headers['User-Agent'] = 'EasyAPIGIS/1.0'
        
        response = requests.get(url, headers=target_headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar URL: {str(e)}")

class InferenceRequest(BaseModel):
    sample: Dict[str, Any]

@app.post("/infer")
def infer_schema(request: InferenceRequest):
    """
    Recebe um JSON (uma linha ou feature) e usa IA para detectar a estrutura.
    """
    if not request.sample:
        raise HTTPException(status_code=400, detail="Amostra vazia.")
    
    result = infer_schema_from_sample(request.sample)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["details"])
        
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import duckdb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.llm import infer_schema_from_sample


app = FastAPI(
    title="EasyAPIGIS Middleware",
    description="Smart API Gateway for Geospatial Data Inference",
    version="0.1.0"
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
        # Teste simples no DuckDB em memória
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

class InferenceRequest(BaseModel):
    sample: Dict[str, Any]

@app.post("/infer")
def infer_schema(request: InferenceRequest):
    """
    Recebe um JSON (uma linha ou feature) e usa IA para detectar a estrutura.
    """
    if not request.sample:
        raise HTTPException(status_code=400, detail="Amostra vazia.")
    
    # Chama a função importada do serviço de IA
    result = infer_schema_from_sample(request.sample)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["details"])
        
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
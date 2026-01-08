import duckdb
from fastapi import FastAPI
from pydantic import BaseModel

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
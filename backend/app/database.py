import os
import asyncpg
from fastapi import HTTPException

# Pega a URL do docker-compose ou usa localhost como fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/easyapigis_db")

async def get_db_connection():
    """
    Retorna uma conexão ativa com o PostGIS.
    """
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar no DB: {e}")
        # Em produção, não retorne o erro cru para o cliente por segurança
        raise HTTPException(status_code=500, detail="Database Connection Failed")

async def init_db():
    """
    Cria os schemas necessários no banco ao iniciar.
    """
    conn = await get_db_connection()
    try:
        # Habilita PostGIS (já vem na imagem, mas garante)
        await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        # Cria schema para dados do usuário
        await conn.execute("CREATE SCHEMA IF NOT EXISTS layers;")
        print("Database initialized (PostGIS + layers schema).")
    except Exception as e:
        print(f"Erro ao inicializar DB: {e}")
    finally:
        await conn.close()
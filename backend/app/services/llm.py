import json
import os
from groq import Groq
from app.config import settings

def infer_schema_from_sample(data_sample: dict) -> dict:
    """
    Usa Llama 3 (via Groq) para inferir o esquema de dados geográficos.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        print("ERRO: GROQ_API_KEY não encontrada.")
        return {"error": "Configuração ausente"}

    # Inicializa o cliente Groq
    client = Groq(api_key=api_key)

    # Prompt otimizado para Llama 3
    system_instruction = "Você é um especialista em GIS e Engenharia de Dados. Responda APENAS com JSON válido."
    
    user_prompt = f"""
    Analise esta amostra de dados JSON:
    {json.dumps(data_sample, indent=2)}

    Tarefa:
    1. Identifique campos de geometria (lat, lon, wkt, geojson).
    2. Identifique o SRID (4326 se for lat/lon).
    3. Sugira nomes de colunas SQL (snake_case).
    4. Tipos SQL: TEXT, INTEGER, FLOAT, TIMESTAMP, BOOLEAN, GEOMETRY.

    Retorne APENAS um objeto JSON com esta estrutura exata, sem explicações:
    {{
        "geometry_field": "nome_campo_original",
        "geometry_type": "POINT/POLYGON",
        "srid": 4326,
        "fields": [
            {{ "original_name": "nm_x", "target_name": "nome_x", "type": "TEXT" }}
        ]
    }}
    """

    try:
        print("Enviando requisição para Groq (Llama 3)...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant", # Modelo rápido e gratuito
            temperature=0.1, # Baixa temperatura para respostas determinísticas
        )

        response_text = chat_completion.choices[0].message.content.strip()
        
        # Limpeza de markdown caso a IA coloque ```json ... ```
        if "```" in response_text:
            response_text = response_text.replace("```json", "").replace("```", "")
        
        print(f"Resposta Groq: {response_text[:50]}...")
        return json.loads(response_text)

    except Exception as e:
        print(f"ERRO Groq: {e}")
        return {"error": "Falha na inferência IA", "details": str(e)}
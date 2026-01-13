import json
import os
import copy
from groq import Groq
from app.config import settings

def sanitize_for_token_limit(data: dict) -> dict:
    """
    Remove arrays gigantes de coordenadas para não estourar o limite de tokens da IA.
    Mantém a estrutura lógica para inferência, mas remove o peso dos dados vetoriais.
    """
    # Faz uma cópia para não alterar o original
    clean_data = copy.deepcopy(data)

    # Função recursiva para limpar listas grandes
    def truncate_large_lists(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Se for campo de coordenadas padrão GeoJSON
                if key in ["coordinates", "geometries"] and isinstance(value, list):
                    obj[key] = ["...[coordinates_truncated_for_ai_analysis]..."]
                # Se for WKT muito longo (String)
                elif isinstance(value, str) and len(value) > 200 and ("POLYGON" in value or "MULTIPOLYGON" in value):
                    obj[key] = value[:50] + "...[wkt_truncated]..."
                else:
                    truncate_large_lists(value)
        elif isinstance(obj, list):
            # Se a lista for muito grande (ex: lista de features), pega só o primeiro
            if len(obj) > 1:
                del obj[1:] 
            for item in obj:
                truncate_large_lists(item)
    
    try:
        truncate_large_lists(clean_data)
        return clean_data
    except Exception as e:
        print(f"Erro ao sanitizar amostra: {e}")
        return data # Em caso de erro, retorna original (arriscando estourar)

def infer_schema_from_sample(data_sample: dict) -> dict:
    """
    Usa Llama 3 (via Groq) para inferir o esquema de dados geográficos.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        print("ERRO: GROQ_API_KEY não encontrada.")
        return {"error": "Configuração ausente"}

    # --- NOVO: Limpeza de Tokens ---
    # Reduz o tamanho do JSON drasticamente antes de enviar
    sanitized_sample = sanitize_for_token_limit(data_sample)
    print("Amostra sanitizada enviada para IA (Tokens economizados).")
    # -------------------------------

    client = Groq(api_key=api_key)

    system_instruction = "Você é um especialista em GIS e Engenharia de Dados. Responda APENAS com JSON válido."
    
    user_prompt = f"""
    Analise esta amostra de dados JSON (os arrays de coordenadas foram truncados intencionalmente):
    {json.dumps(sanitized_sample, indent=2)}

    Tarefa:
    1. Identifique campos de geometria (lat, lon, wkt, geojson, coordinates).
       Nota: Se vir "coordinates_truncated", assuma que é geometria válida (POINT/POLYGON).
    2. Identifique o SRID (4326 se for lat/lon ou GeoJSON padrão).
    3. Sugira nomes de colunas SQL (snake_case).
    4. Tipos SQL: TEXT, INTEGER, FLOAT, TIMESTAMP, BOOLEAN, GEOMETRY.

    Retorne APENAS um objeto JSON com esta estrutura exata, sem explicações:
    {{
        "geometry_field": "nome_campo_original",
        "geometry_type": "POINT/POLYGON/MULTIPOLYGON",
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
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=1024, # Limita a resposta também para economizar
        )

        response_text = chat_completion.choices[0].message.content.strip()
        
        if "```" in response_text:
            response_text = response_text.replace("```json", "").replace("```", "")
        
        print(f"Resposta Groq recebida com sucesso.")
        return json.loads(response_text)

    except Exception as e:
        print(f"ERRO Groq: {e}")
        return {"error": "Falha na inferência IA", "details": str(e)}
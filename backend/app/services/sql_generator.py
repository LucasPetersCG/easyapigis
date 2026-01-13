import re

def sanitize_name(name: str) -> str:
    """
    Remove caracteres perigosos para evitar SQL Injection e erros de sintaxe.
    Permite apenas letras, números e underscores.
    """
    # Substitui espaços e hífens por underscore
    clean = re.sub(r'[\s-]', '_', name.lower())
    # Remove tudo que não for alfanumérico ou underscore
    clean = re.sub(r'[^a-z0-9_]', '', clean)
    # Garante que não comece com número
    if clean and clean[0].isdigit():
        clean = f"t_{clean}"
    return clean

def generate_ddl(table_name: str, schema_info: dict) -> str:
    """
    Gera o comando SQL CREATE TABLE baseado no schema inferido pela IA.
    """
    safe_table = sanitize_name(table_name)
    
    fields_sql = []
    
    # 1. Processar Colunas Normais
    for field in schema_info.get("fields", []):
        f_name = sanitize_name(field["target_name"])
        f_type_raw = field["type"].upper()
        
        # Mapeamento IA -> PostgreSQL
        pg_type = "TEXT"
        if "INT" in f_type_raw: pg_type = "INTEGER"
        elif "FLOAT" in f_type_raw or "DOUBLE" in f_type_raw: pg_type = "DOUBLE PRECISION"
        elif "BOOL" in f_type_raw: pg_type = "BOOLEAN"
        elif "TIME" in f_type_raw or "DATE" in f_type_raw: pg_type = "TIMESTAMP"
        
        fields_sql.append(f"{f_name} {pg_type}")
    
    # 2. Processar Geometria (PostGIS)
    srid = schema_info.get("srid", 4326)
    geo_type = schema_info.get("geometry_type", "POINT").upper()
    
    # Adiciona coluna de geometria espacial
    fields_sql.append(f"geom GEOMETRY({geo_type}, {srid})")
    
    # 3. Montar SQL Final
    columns_block = ",\n    ".join(fields_sql)
    
    ddl = f"""
    CREATE TABLE IF NOT EXISTS layers.{safe_table} (
        id SERIAL PRIMARY KEY,
        {columns_block}
    );
    """
    return ddl
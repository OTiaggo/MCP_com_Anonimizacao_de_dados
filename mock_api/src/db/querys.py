from src.db.conection import get_db_connection
from psycopg2.extras import RealDictCursor


# ==========================================
# ENDPOINT 1: Descontos Realizados
# ==========================================
def desconto_realizado_query(FORNECEDOR: str, VAREJISTA: str):
    conn = get_db_connection()
    # Usamos RealDictCursor para receber os dados como dicionário, não tupla
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            id, 
            data_operacao, 
            valor_desconto 
        FROM descontos_realizados 
        WHERE fornecedor = %s AND varejista = %s
        ORDER BY data_operacao DESC;
    """
    
    # O segundo argumento deve ser uma tupla (param1, param2)
    # Isso previne SQL Injection automaticamente
    cur.execute(query, (FORNECEDOR, VAREJISTA))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Se não achar nada, retorna lista vazia ou 404 (opcional)
    if not rows:
        return {"message": "Nenhum desconto encontrado para este par.", "data": []}

    return {"data": rows}



# ==========================================
# ENDPOINT 2: Descontos Calculados
# ==========================================
def desconto_calculado_query(FORNECEDOR: str, VAREJISTA: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            id, 
            data_calculo, 
            valor_calculado 
        FROM descontos_calculados 
        WHERE fornecedor = %s AND varejista = %s
        ORDER BY data_calculo DESC;
    """
    
    cur.execute(query, (FORNECEDOR, VAREJISTA))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    if not rows:
        return {"message": "Nenhum cálculo encontrado para este par.", "data": []}

    return {"data": rows}



# ==========================================
# ENDPOINT 3: Mapeamento de Organizações (Tabela Completa)
# ==========================================
def get_organization_mappings():
    conn = get_db_connection()
    # Usamos RealDictCursor para retornar como lista de dicionários
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            organizacao, 
            variavel 
        FROM organization_mappings
        ORDER BY organizacao ASC;
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Validação simples
    if not rows:
        return {"message": "Nenhuma organização cadastrada.", "data": []}

    return {"data": rows}
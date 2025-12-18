from typing import Union
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor

from src.db.conection import get_db_connection
from src.db.querys import desconto_realizado_query, desconto_calculado_query, get_organization_mappings


app = FastAPI()


# ==========================================
# ENDPOINT 1: Descontos Realizados
# ==========================================
@app.get("/desconto_realizado/{FORNECEDOR}/{VAREJISTA}")
def desconto_realizado(FORNECEDOR: str, VAREJISTA: str):
    return desconto_realizado_query(FORNECEDOR, VAREJISTA)

# ==========================================
# ENDPOINT 2: Descontos Calculados
# ==========================================
@app.get("/desconto_calculado/{FORNECEDOR}/{VAREJISTA}")
def desconto_calculado(FORNECEDOR: str, VAREJISTA: str):
    return desconto_calculado_query(FORNECEDOR, VAREJISTA)

@app.get("/tabelaDeVariaveis")
def tabela_de_variaveis():
    return get_organization_mappings()

@app.get("/teste")
def teste():
    return {"message": "Teste bem-sucedido!"}
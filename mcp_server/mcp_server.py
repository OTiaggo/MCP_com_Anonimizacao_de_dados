from mcp.server.fastmcp import FastMCP
import httpx
import os

# Cria o servidor "tudo em um"
mcp = FastMCP("desconto-api-server")

API_BASE_URL = os.getenv("API_BASE_URL", "http://mock_api:8000")

@mcp.tool()
async def desconto_realizado(fornecedor: str, varejista: str) -> str:
    """Busca descontos já realizados entre fornecedor e varejista"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/desconto_realizado/{fornecedor}/{varejista}")
        return str(resp.json())

@mcp.tool()
async def desconto_calculado(fornecedor: str, varejista: str) -> str:
    """Calcula descontos potenciais entre fornecedor e varejista"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/desconto_calculado/{fornecedor}/{varejista}")
        return str(resp.json())

@mcp.tool()
async def tabela_variaveis() -> str:
    """Retorna a tabela completa de variáveis"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/tabelaDeVariaveis")
        return str(resp.json())

if __name__ == "__main__":
    import uvicorn
    
    # Em vez de usar mcp.run(), pegamos a aplicação SSE interna e rodamos com Uvicorn
    # Isso evita erros de argumentos e garante que o Docker consiga expor a porta
    print(f"🚀 Iniciando servidor FastMCP (SSE) na porta {8080}...")
    
    # mcp.sse_app() retorna uma aplicação Starlette configurada com a rota /sse
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8080)
import httpx
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import Resource, Tool
from mcp.types import (
    TextContent, ImageContent, EmbeddingContent, ListToolsResult, ListResourcesResult
)
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações da API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

server = Server("desconto-api-server")

class DescontoRequest(BaseModel):
    fornecedor: str = Field(..., description="Nome do fornecedor")
    varejista: str = Field(..., description="Nome do varejista")

class VariaveisResponse(BaseModel):
    variaveis: List[Dict[str, Any]]

# ==========================================
# TOOLS - Recursos principais da API
# ==========================================

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """Lista todas as ferramentas disponíveis."""
    return ListToolsResult(tools=[
        Tool(
            name="desconto_realizado",
            description="Busca descontos já realizados entre fornecedor e varejista",
            inputSchema=DescontoRequest.model_json_schema()
        ),
        Tool(
            name="desconto_calculado", 
            description="Calcula descontos potenciais entre fornecedor e varejista",
            inputSchema=DescontoRequest.model_json_schema()
        ),
        Tool(
            name="tabela_variaveis",
            description="Retorna a tabela completa de variáveis/mapeamentos de organizações",
            inputSchema={}
        )
    ])

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> ListContent:
    """Executa as ferramentas da API."""
    
    async with httpx.AsyncClient() as client:
        try:
            if name == "desconto_realizado":
                fornecedor = arguments["fornecedor"]
                varejista = arguments["varejista"]
                response = await client.get(f"{API_BASE_URL}/desconto_realizado/{fornecedor}/{varejista}")
                
            elif name == "desconto_calculado":
                fornecedor = arguments["fornecedor"]
                varejista = arguments["varejista"]
                response = await client.get(f"{API_BASE_URL}/desconto_calculado/{fornecedor}/{varejista}")
                
            elif name == "tabela_variaveis":
                response = await client.get(f"{API_BASE_URL}/tabelaDeVariaveis")
                
            else:
                return ListContent(contents=[
                    TextContent(type="text", text=f"Tool '{name}' não encontrada")
                ])
            
            response.raise_for_status()
            data = response.json()
            
            # Formata resposta como texto legível
            if isinstance(data, list):
                formatted = "\n".join([str(item) for item in data])
            elif isinstance(data, dict):
                formatted = str(data)
            else:
                formatted = str(data)
                
            return ListContent(contents=[
                TextContent(type="text", text=f"✅ **Resultado {name}:**\n```\n{formatted}\n```")
            ])
            
        except httpx.HTTPStatusError as e:
            return ListContent(contents=[
                TextContent(type="text", text=f"❌ Erro HTTP {e.response.status_code}: {e.response.text}")
            ])
        except Exception as e:
            return ListContent(contents=[
                TextContent(type="text", text=f"❌ Erro: {str(e)}")
            ])

# ==========================================
# RESOURCES - Dados adicionais (opcional)
# ==========================================

@server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """Lista recursos disponíveis (metadata da API)."""
    return ListResourcesResult(resources=[
        Resource(
            uri="desconto-api://info",
            name="Informações da API de Descontos",
            description="API para consulta de descontos realizados e calculados entre fornecedores e varejistas",
            mimeType="text/markdown"
        )
    ])

@server.read_resource()
async def handle_read_resource(uri: str) -> ListContent:
    """Retorna informações sobre a API."""
    if uri == "desconto-api://info":
        info = """
# 📊 API de Descontos - Ferramentas Disponíveis

## 🛠️ Ferramentas:

**`desconto_realizado`**  
Consulta descontos já realizados  
*Parâmetros:* `fornecedor`, `varejista`

**`desconto_calculado`**  
Calcula descontos potenciais  
*Parâmetros:* `fornecedor`, `varejista`

**`tabela_variaveis`**  
Tabela completa de variáveis/mapeamentos

## 🔗 Endpoints Originais:
- `GET /desconto_realizado/{FORNECEDOR}/{VAREJISTA}`
- `GET /desconto_calculado/{FORNECEDOR}/{VAREJISTA}`
- `GET /tabelaDeVariaveis`
        """
        return ListContent(contents=[
            TextContent(type="text", text=info)
        ])
    
    return ListContent(contents=[
        TextContent(type="text", text="Recurso não encontrado")
    ])

if __name__ == "__main__":
    print(f"🚀 Servidor MCP rodando em: {API_BASE_URL}")
    server.run()
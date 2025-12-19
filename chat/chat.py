import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client import ClientSession
import httpx
from typing import List, Dict, Any

load_dotenv()

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MCP_URL = os.getenv("MCP_URL", "http://localhost:8001")  # URL do seu servidor MCP

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class MCPChat:
    def __init__(self):
        self.mcp_session = None
        self.tools = []
        
    async def connect_mcp(self):
        """Conecta ao servidor MCP e carrega ferramentas"""
        self.mcp_session = ClientSession()
        await self.mcp_session.connect(MCP_URL)
        
        # Lista ferramentas disponíveis
        tools_result = await self.mcp_session.list_tools()
        self.tools = tools_result.tools
        
        print(f"✅ Conectado ao MCP! {len(self.tools)} ferramentas carregadas:")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")
        print()

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Chama ferramenta MCP"""
        result = await self.mcp_session.call_tool(tool_name, arguments)
        return result.contents[0].text if result.contents else "Sem resultado"

    async def chat(self):
        """Loop principal do chat"""
        print("🤖 Chat GPT-4o-mini + MCP Descontos API")
        print("Digite 'quit' para sair\n")
        
        messages = [
            {
                "role": "system",
                "content": """Você é um assistente especializado em análise de descontos entre fornecedores e varejistas.
                
Ferramentas disponíveis:
- desconto_realizado: Busca descontos já realizados
- desconto_calculado: Calcula descontos potenciais  
- tabela_variaveis: Lista todas as variáveis/mapeamentos

Sempre pergunte fornecedor e varejista quando necessário. Use as ferramentas MCP automaticamente para obter dados reais da API."""
            }
        ]
        
        while True:
            user_input = input("Você: ").strip()
            if user_input.lower() in ['quit', 'exit', 'sair']:
                break
                
            messages.append({"role": "user", "content": user_input})
            
            # Chama GPT-4o-mini com ferramentas MCP
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=[tool.model_dump() for tool in self.tools],
                tool_choice="auto",
                temperature=0.1,
                max_tokens=2000
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # Processa chamadas de ferramentas
            if response_message.tool_calls:
                print("\n🛠️  Executando ferramentas...")
                
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"🔄 Chamando {tool_name}...")
                    tool_result = await self.call_mcp_tool(tool_name, arguments)
                    
                    # Adiciona resultado da ferramenta aos messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                    
                    print(f"✅ {tool_name}: {tool_result[:200]}...")
                
                # Segunda chamada para resposta final
                final_response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.1
                )
                
                final_content = final_response.choices[0].message.content
                print(f"\n🤖 GPT-4o-mini: {final_content}")
                messages.append({"role": "assistant", "content": final_content})
                
            else:
                print(f"\n🤖 GPT-4o-mini: {response_message.content}")
            
            print("-" * 80)

async def main():
    chat = MCPChat()
    
    try:
        await chat.connect_mcp()
        await chat.chat()
    except KeyboardInterrupt:
        print("\n👋 Chat encerrado!")
    finally:
        if chat.mcp_session:
            await chat.mcp_session.close()

if __name__ == "__main__":
    asyncio.run(main())
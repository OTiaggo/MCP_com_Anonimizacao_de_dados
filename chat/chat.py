import os
import asyncio
import json
import traceback
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

# Carrega .env forçando override para garantir que pegue a chave nova
load_dotenv(override=True)

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MCP_URL = os.getenv("MCP_URL", "http://localhost:8080/sse") 

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def run_chat():
    print(f"📡 Conectando ao servidor MCP em: {MCP_URL}...")

    try:
        async with sse_client(MCP_URL) as streams:
            read_stream, write_stream = streams
            
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # 1. Carregar Ferramentas
                tools_result = await session.list_tools()
                tools = tools_result.tools
                
                print(f"✅ Conectado! {len(tools)} ferramentas disponíveis:")
                for t in tools:
                    print(f"  - {t.name}: {t.description}")
                print("\n🤖 Chat Iniciado (Digite 'sair' para encerrar)")
                print("-" * 50)

                messages = [{
                    "role": "system", 
                    "content": "Você é um auditor útil. Use as ferramentas disponíveis para consultar dados."
                }]

                # 2. Loop do Chat
                while True:
                    try:
                        user_input = input("\nVocê: ").strip()
                        if user_input.lower() in ['sair', 'exit', 'quit']:
                            break
                        
                        messages.append({"role": "user", "content": user_input})
                        
                        # Chama GPT (CORREÇÃO AQUI: Formatando tools para OpenAI)
                        response = await client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            tools=[{
                                "type": "function",
                                "function": {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "parameters": tool.inputSchema
                                }
                            } for tool in tools],
                            tool_choice="auto"
                        )
                        
                        ai_msg = response.choices[0].message
                        messages.append(ai_msg)

                        # Verifica se a IA quer usar ferramentas
                        if ai_msg.tool_calls:
                            print("🛠️  A IA está consultando o sistema...")
                            
                            for tool_call in ai_msg.tool_calls:
                                name = tool_call.function.name
                                args = json.loads(tool_call.function.arguments)
                                
                                # Executa a ferramenta no servidor MCP
                                result = await session.call_tool(name, args)
                                tool_output = result.content[0].text
                                
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": tool_output
                                })
                                print(f"  > Retorno de {name}: {tool_output[:100]}...")

                            # Segunda chamada para a IA formular a resposta final
                            final = await client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=messages
                            )
                            final_msg = final.choices[0].message.content
                            print(f"🤖 IA: {final_msg}")
                            messages.append({"role": "assistant", "content": final_msg})
                        
                        else:
                            print(f"🤖 IA: {ai_msg.content}")

                    except KeyboardInterrupt:
                        break
                        
    except Exception as e:
        print(f"\n❌ Erro Fatal:")
        traceback.print_exc()
        print(f"Mensagem: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_chat())
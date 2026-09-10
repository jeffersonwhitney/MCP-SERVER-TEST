import asyncio
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()

# Inicializamos a nossa IA exatamente como fizemos na trilha de Tool Calling
client_llm = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

async def rodar_cliente():
    url_servidor = "http://localhost:8000/sse"
    print(f"[CLIENTE] Conectando ao servidor MCP em {url_servidor}...")
    
    async with sse_client(url_servidor) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # 1. Descobrimos o que o servidor sabe fazer
            lista_ferramentas = await session.list_tools()
            
            # 2. Traduzimos as ferramentas do MCP para o formato que a IA entende
            tools_para_ia = []
            for tool in lista_ferramentas.tools:
                tools_para_ia.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            # 3. Simulamos a pergunta do usuário
            pergunta = "Preciso montar um orçamento, qual o valor atualizado do produto PROD02 na matriz?"
            print(f"\n[USUÁRIO]: {pergunta}")
            
            # Enviamos para a DeepSeek
            response = client_llm.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": pergunta}],
                tools=tools_para_ia, # A IA recebe as ferramentas que vieram do servidor web!
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # 4. O laço de execução: A IA decide chamar a ferramenta
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    nome_funcao = tool_call.function.name
                    argumentos = json.loads(tool_call.function.arguments)
                    
                    print(f"\n[DECISÃO DA IA]: A IA pediu para executar '{nome_funcao}' com {argumentos}")
                    
                    # 5. O CLIENTE pede pro SERVIDOR rodar a função via MCP
                    resultado_mcp = await session.call_tool(nome_funcao, arguments=argumentos)
                    
                    # Extraímos o texto do resultado que o servidor MCP devolveu
                    texto_resultado = "\n".join(c.text for c in resultado_mcp.content if c.type == "text")
                    
                    print(f"[RETORNO DO SERVIDOR]: {texto_resultado}")
            else:
                print("A IA respondeu sem usar ferramentas.")

if __name__ == "__main__":
    asyncio.run(rodar_cliente())
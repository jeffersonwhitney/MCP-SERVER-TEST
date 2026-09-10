import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def rodar_cliente():
    url_servidor = "http://localhost:8000/sse"
    print(f"[CLIENTE] Tentando conectar no servidor MCP em {url_servidor}...")
    
    # Estabelece a conexão SSE com o servidor
    async with sse_client(url_servidor) as (read_stream, write_stream):
        # Inicia a sessão MCP
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("[CLIENTE] Conexão estabelecida com sucesso!\n")
            
            print("--- FERRAMENTAS DESCOBERTAS NO SERVIDOR ---")
            # Lista as ferramentas de forma dinâmica (Harness)
            lista_ferramentas = await session.list_tools()
            
            for tool in lista_ferramentas.tools:
                print(f"🔧 Nome: {tool.name}")
                print(f"📝 Descrição: {tool.description}")
                print(f"⚙️  Schema (Parâmetros): {tool.inputSchema}\n")

if __name__ == "__main__":
    # Roda o laço assíncrono do cliente
    asyncio.run(rodar_cliente())
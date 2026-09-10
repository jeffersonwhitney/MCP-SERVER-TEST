from mcp.server.fastmcp import FastMCP

# Inicializa o servidor FastMCP com um nome amigável
mcp = FastMCP("ServidorDeDadosGerais")

# Ferramenta 1: Leitura de dados (Exemplo: Tabela de preços)
@mcp.tool()
def consultar_preco_produto(codigo_produto: str) -> str:
    """
    Consulta o preço atualizado de um produto no banco de dados.
    Use esta ferramenta SEMPRE que precisar informar um preço.
    """
    tabela_precos = {
        "PROD01": "R$ 150,00",
        "PROD02": "R$ 3.500,00"
    }
    
    # Validação simples para evitar quebra caso o código não exista
    preco = tabela_precos.get(codigo_produto.upper())
    if preco:
        return f"O produto {codigo_produto} custa {preco}."
    else:
        return f"Erro: Produto {codigo_produto} não encontrado na base de dados."

# Ferramenta 2: Leitura de dados (Exemplo: Verificação de agenda)
@mcp.tool()
def verificar_disponibilidade_agenda(data_consulta: str) -> str:
    """
    Verifica a disponibilidade da equipe em uma data específica.
    Formato esperado da data_consulta: DD/MM/AAAA.
    """
    # Simulando um banco de dados de agenda
    dias_ocupados = ["10/10/2026", "11/10/2026", "12/10/2026"]
    
    if data_consulta in dias_ocupados:
        return f"A equipe não está disponível na data {data_consulta}."
    
    return f"A data {data_consulta} está livre para agendamentos."

if __name__ == "__main__":
    print("Iniciando servidor MCP via SSE...")
    mcp.run(transport="sse")
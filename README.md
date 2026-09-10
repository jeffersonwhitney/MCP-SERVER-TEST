# Servidor MCP (Model Context Protocol) - Leitura de Dados Comerciais

Este repositório implementa a arquitetura Cliente-Servidor utilizando o Model Context Protocol (MCP) via Server-Sent Events (SSE). 

## Mapeamento de Risco (Risk Assessment)

Em conformidade com as diretrizes de segurança de agentes LLM, a separação de escopo entre **Tools de Leitura (Read)** e **Tools de Escrita (Write)** é o pilar de defesa do sistema. A IA atua como um agente não determinístico e suscetível a *Prompt Injections* ou alucinações de contexto. O código abaixo avalia os riscos da atual implementação e os perigos potenciais de escalonamento de privilégios.

### 1. Riscos das Ferramentas Atuais (Leitura / GET)
O servidor atual expõe apenas dados via métodos de leitura. O risco associado é exclusivamente de **Exposição de Informação (Data Leakage)**, sem risco de integridade.
* **`consultar_preco_produto`:** Acessa a matriz de preços comerciais. Se a tool for usada indevidamente por um agente exposto externamente, a estratégia de precificação, os descontos por região (ex: praças comerciais de João Pessoa) e os valores de custo poderão ser vazados para concorrentes. O estado do banco de dados, no entanto, permanece intacto.
* **`verificar_disponibilidade_agenda`:** Acessa a ocupação e alocação da equipe operacional. O risco é o mapeamento não autorizado da capacidade logística da empresa, o que é classificado como risco baixo/médio dependendo do grau de sigilo da operação.

### 2. O Risco Crítico das Ferramentas de Escrita (Write / POST / UPDATE)
Caso o servidor atual fosse expandido para incluir ferramentas de escrita (ex: `aplicar_desconto_matriz` ou `reagendar_rota_comercial`), o agente ganharia o poder de alterar o estado do sistema. 
* **O Perigo da Delegação Cega:** Como o servidor apenas valida a estrutura dos parâmetros de input (ex: garantir que a porcentagem de desconto é um número float), o código em si é executado perfeitamente. Contudo, se a IA sofrer uma alucinação de contexto (ex: confundir um teste com produção) ou for manipulada por um texto malicioso no corpo de um e-mail, ela poderá disparar comandos estruturalmente perfeitos, mas operacionalmente desastrosos. 
* **Impacto Simulado:** A IA poderia reduzir o preço de todos os produtos do ERP para R$ 0,01 ou apagar os registros da rota comercial inteira do mês.
* **Mitigação Implementada:** A defesa arquitetural adotada neste projeto é o *Princípio do Menor Privilégio*: não expor ferramentas de escrita onde ferramentas de leitura bastam, e segregar servidores MCP por nível de risco.

## Integração do Cliente (Harness) e Orquestração do LLM

O repositório contempla o fluxo completo de interação entre o protocolo MCP e um Large Language Model (LLM), utilizando a arquitetura de delegação de chamadas.

### 3. Descoberta Dinâmica de Ferramentas
O módulo cliente estabelece uma conexão via Server-Sent Events (SSE) e executa a varredura das capacidades do servidor sem possuir conhecimento estrutural prévio. Através do método de inicialização de sessão, o cliente resgata o JSON Schema de cada ferramenta mapeada (nome, descrição e parâmetros) e efetua a tradução em tempo de execução para o padrão nativo exigido pela SDK da OpenAI.

### 4. O Ciclo de Execução Agente-Servidor
A orquestração consolida a ponte entre o raciocínio semântico e a execução determinística local através de quatro etapas:
1. O LLM recebe a requisição do usuário final anexada às descrições das ferramentas recém-descobertas no servidor web.
2. O modelo determina autonomamente a necessidade de buscar dados externos e emite o *Tool Call*.
3. O cliente intercepta a requisição, envia o comando de execução de volta ao servidor MCP via HTTP, e aguarda o processamento.
4. O resultado estruturado é devolvido ao contexto da IA, que processa a saída bruta do sistema e compila a resposta final.
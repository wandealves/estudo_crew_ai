from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool

class SQLQueryCrew:
    """
    Classe para organizar agentes, tarefas e a execução da geração de consultas SQL.
    """

    def __init__(self):
        load_dotenv()  # Carregar variáveis de ambiente
        self.llm = "gpt-4o-mini"  # Definir o modelo de linguagem usado pelo agente

        self.schema_tool = FileReadTool()
        self.crew = None  # Será inicializado no create_crew()

        # Criar a Crew no momento da inicialização
        self.create_crew()

    def create_crew(self):
        """Cria os agentes, tarefas e a CrewAI."""

        # Criando o agente especialista em SQL
        self.sql_agent = Agent(
            role="Especialista em SQL",
            goal="Gerar consultas SQL precisas e otimizadas para diferentes bancos de dados.",
            backstory=(
                "Você é um renomado especialista em SQL, com conhecimento avançado em diversas bases de dados, incluindo Postgres, MySQL e SQL Server. "
                "Sua missão é interpretar descrições textuais e transformá-las em consultas SQL eficientes, sempre considerando a estrutura do banco de dados."
            ),
            tools=[self.schema_tool],
            verbose=True,
            memory=True,
            llm=self.llm
        )

        # Criando a tarefa que o agente executará
        self.task = Task(
            description=(
                r"""A partir do meu gerenciador {database_type}, 
                no banco de dados '{database_name}',
                e do esquema fornecido no arquivo 
                YAML localizado em {yaml_path}, 
                gere uma consulta SQL otimizada para 
                atender ao seguinte pedido: 
                
                {user_request}. 
                
                Certifique-se de usar as tabelas e colunas 
                corretas conforme a estrutura do YAML.
                
                O valor inserido em `json_output` é {json_output}.
                
                IMPORTANTE:
                - **Formato de Retorno:**  
                  Se `json_output` for **True**, a consulta deve retornar os dados em formato JSON, 
                  usando as funções apropriadas para cada banco de dados:  
                    - **Postgres:** `row_to_json()` ou `json_agg()`  
                    - **MySQL:** `JSON_OBJECT()` ou `JSON_ARRAYAGG()`  
                    - **SQL Server:** `FOR JSON AUTO`  
                    - **Oracle:** `JSON_OBJECT()`  
                  Caso contrário, a consulta deve ser otimizada para um **retorno tabular tradicional**.

                - **Otimização:**  
                  - Sempre utilize **índices disponíveis** para melhorar a performance.  
                  - Se houver junções (`JOINs`), prefira **chaves indexadas** para evitar scans desnecessários.  
                  - Ordene os resultados de maneira lógica se necessário (`ORDER BY`).  
                  
                - **Considerações Específicas:**  
                  - Evite selecionar colunas desnecessárias (`SELECT *` não é recomendado).  
                  - Se a consulta precisar de filtros (`WHERE`), utilize os campos de indexação do banco de dados para maior eficiência.  
                  - Para valores nulos, utilize funções adequadas como `COALESCE()` para garantir legibilidade no resultado.  
                  
                """
            ),
            expected_output="Uma consulta SQL válida e otimizada para o banco de dados especificado.",
            agent=self.sql_agent
        )

        # Criando a equipe com o agente e a tarefa
        self.crew = Crew(
            agents=[self.sql_agent],
            tasks=[self.task],
            process=Process.sequential  # A execução será sequencial
        )

    def kickoff(self, inputs):
        """
        Executa o processo de geração de consultas SQL.

        Args:
            inputs (dict): Dicionário contendo os parâmetros de entrada:
                - database_type (str): Tipo do banco de dados (Postgres, MySQL, etc.).
                - database_name (str): Nome do banco de dados.
                - yaml_path (str): Caminho do arquivo YAML contendo a estrutura do banco.
                - user_request (str): Pedido textual para gerar a consulta SQL.
                - json_output (bool): Define se a consulta deve retornar um JSON ou um formato tabular.

        Returns:
            str: A consulta SQL gerada no formato esperado.
        """
        result = self.crew.kickoff(inputs=inputs).raw
        result = result.replace("sql","")  # Remover as crases triplas para evitar problemas com formatação de código
        result = result.replace("```", "")  # Remover as crases triplas para evitar problemas com formatação de código
        
        return result
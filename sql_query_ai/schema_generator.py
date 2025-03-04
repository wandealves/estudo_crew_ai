import os
import yaml
from psycopg2 import sql
from postgres_connection import PostgresConnection  # Sua classe de conexão
from postgres_databases import PostgresDatabases  # Definições dos bancos

class SchemaTool:
    """
    Ferramenta para extrair informações do schema e gerar YAMLs.
    """

    def __init__(self, database_uri, categorical_columns=None):
        """
        Inicializa com a URI do banco e um dicionário de colunas categóricas.

        :param database_uri: URI de conexão do PostgreSQL.
        :param categorical_columns: Dicionário onde as chaves são tabelas e os valores são listas de colunas categóricas.
        """
        self.db = PostgresConnection(database_uri)
        self.categorical_columns = categorical_columns if categorical_columns else {}

    def connect(self):
        """ Estabelece a conexão com o banco de dados. """
        self.db.connect()

    def disconnect(self):
        """ Fecha a conexão com o banco de dados. """
        self.db.disconnect()

    def list_tables_and_columns(self):
        """
        Retorna um dicionário com as tabelas, colunas e possíveis valores (apenas categóricos).
        """
        sql_query = """
        SELECT 
            table_schema,
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name, ordinal_position;
        """
        cursor = self.db.cursor
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        schema_info = {}
        for schema, table, column, dtype, nullable in rows:
            if schema not in schema_info:
                schema_info[schema] = {}
            if table not in schema_info[schema]:
                schema_info[schema][table] = []

            column_def = {
                "column_name": column,
                "data_type": dtype,
                "is_nullable": nullable
            }

            # 🔥 Se a tabela está na lista categórica e a coluna foi definida, busca os valores distintos
            if table in self.categorical_columns and column in self.categorical_columns[table]:
                distinct_vals = self.get_distinct_values(schema, table, column)
                if distinct_vals:
                    column_def["possible_values"] = distinct_vals

            schema_info[schema][table].append(column_def)
        return schema_info

    def get_distinct_values(self, schema, table, column, limit=50):
        """
        Obtém valores distintos de uma coluna categórica e inclui o ID.
        """
        # 🛠️ Precisamos descobrir qual é a chave primária da tabela
        primary_key = self.get_primary_key(schema, table)
        if not primary_key:
            print(f"⚠️ Nenhuma chave primária encontrada para a tabela {table}.")
            return []

        # 🔥 Consulta para obter os valores distintos junto com o ID
        sql_query = sql.SQL("""
        SELECT {primary_key}, {column}
        FROM {schema}.{table}
        WHERE {column} IS NOT NULL
        ORDER BY {primary_key}
        LIMIT {limit};
        """).format(
            primary_key=sql.Identifier(primary_key),
            column=sql.Identifier(column),
            schema=sql.Identifier(schema),
            table=sql.Identifier(table),
            limit=sql.Literal(limit)
        )

        cursor = self.db.cursor
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        # ✅ Converter os valores para UTF-8 corretamente e estruturar no formato correto
        return [{"id": row[0], column: str(row[1])} for row in rows]

    def get_primary_key(self, schema, table):
        """
        Obtém o nome da chave primária de uma tabela.
        """
        sql_query = sql.SQL("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = {schema}
          AND tc.table_name = {table};
        """).format(
            schema=sql.Literal(schema),
            table=sql.Literal(table)
        )

        cursor = self.db.cursor
        cursor.execute(sql_query)
        result = cursor.fetchone()
        return result[0] if result else None

    def generate_yaml(self):
        """
        Gera o arquivo YAML para o banco de dados conectado.
        """
        database_name = self.db.get_current_database()
        tables_info = self.list_tables_and_columns()

        final_data = {
            "tables": tables_info
        }

        # Define a pasta e o nome do arquivo
        output_folder = os.path.join(os.getcwd(), "schemas")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"schema_{database_name}.yaml")

        # Salva o YAML no arquivo
        with open(output_file, "w", encoding="utf-8") as yaml_file:
            yaml.dump(final_data, yaml_file, sort_keys=False, default_flow_style=False, allow_unicode=True)
        print(f"✅ YAML gerado com sucesso: {output_file}")

    def kickoff(self):
        """
        Método para executar todo o processo:
        1. Conectar ao banco
        2. Gerar o YAML
        3. Desconectar do banco
        """
        try:
            print("🔌 Conectando ao banco...")
            self.connect()
            print("📂 Gerando arquivo YAML...")
            self.generate_yaml()
        except Exception as e:
            print(f"❌ Erro durante a execução: {e}")
        finally:
            print("🔌 Desconectando do banco...")
            self.disconnect()
            print("✅ Processo concluído!")




if __name__ == "__main__":
    # Definição do banco de dados
    database_uri = PostgresDatabases.ECOMMERCE
    #database_uri = PostgresDatabases.CLINICA

    # Agora podemos definir quais colunas de cada tabela são categóricas!
    """
    categorical_columns = {
        "categorias": ["nome"], 
        "metodos_pagamento": ["nome"],
        "status" : ["nome"]
    }
    """

    
    categorical_columns = {
        "convenios": ["nome"], 
    }
    

    # Criando a instância da ferramenta de schema
    schema_tool = SchemaTool(database_uri=database_uri, categorical_columns=categorical_columns)

    # 🚀 Executando tudo com um só comando!
    schema_tool.kickoff()
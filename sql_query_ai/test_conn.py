from postgres_connection import PostgresConnection  # Certifique-se de que está importando a conexão corretamente
from postgres_databases import PostgresDatabases
from psycopg2 import sql

ecommerce_database = PostgresDatabases.ECOMMERCE

conn = PostgresConnection(database_uri=ecommerce_database)
conn.connect()

print(conn.get_current_database())

cursor = conn.cursor

sql_01 = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'ecommerce';"
cursor.execute(sql_01)
result = cursor.fetchall()  # Obtém os resultados

print(result)  # Exibe a lista de tabelas no esquema 'public'

cursor.execute("SELECT current_database();")
db_name = cursor.fetchone()
print(f"Banco de dados conectado: {db_name[0]}")


sql_02 = "SELECT table_schema, table_name FROM information_schema.tables;"
cursor.execute(sql_02)
result = cursor.fetchall()
print(result)  # Lista todas as tabelas e seus esquemas


sql_query ='SELECT * from "categorias";'

cursor.execute(sql_query)

# Obtendo os resultados
results = cursor.fetchall()

print(results)

i=0
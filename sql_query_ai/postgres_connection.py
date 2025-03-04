import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

load_dotenv()

class PostgresConnection:
    """
    Classe para gerenciar conexões com múltiplos bancos de dados PostgreSQL.
    """

    # Definições de strings de conexão


    def __init__(self, database_uri=None):
        """
        Inicializa com a URI do banco de dados.
        """
        self.conn = None
        self.cursor = None
        self.database_uri = database_uri
        
        
    def connect(self):
        """
        Estabelece a conexão com o banco de dados PostgreSQL.
        """
        try:
            self.conn = psycopg2.connect(self.database_uri)
            self.cursor = self.conn.cursor()
            print(f"[PostgresConnection] Conexão estabelecida com sucesso: {self.database_uri}")
        except OperationalError as e:
            print(f"[PostgresConnection] Erro ao conectar: {str(e)}")
            self.conn = None
            self.cursor = None

    def disconnect(self):
        """
        Desconecta do banco de dados.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_current_database(self):
        """
        Retorna o nome do banco de dados atual usando 'SELECT current_database()'.
        """
        if not self.conn:
            raise ConnectionError("Conexão não estabelecida.")
        self.cursor.execute("SELECT current_database();")
        return self.cursor.fetchone()[0]

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
        
    def get_colunas(self):
        """
        Retorna o nome das colunas da consulta.
        """
        if not self.cursor:
            raise ConnectionError("Cursor não definido.")
        return [desc[0] for desc in self.cursor.description]
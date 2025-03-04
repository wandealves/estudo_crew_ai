import os
from dotenv import load_dotenv

class PostgresDatabases:
    """Classe estática para gerenciar conexões com múltiplos bancos de dados PostgreSQL."""

    # Carrega as variáveis de ambiente uma única vez
    load_dotenv()
    _database_uri = os.getenv("DATABASE_URI", "").rstrip("/")  # Evita barra duplicada

    if not _database_uri:
        raise ValueError("DATABASE_URI não foi definida no ambiente.")

    # Dicionário de mapeamento dos bancos de dados
    _databases = {
        "ecommerce": f"{_database_uri}/ecommerce",
        "clinica": f"{_database_uri}/clinica",
        "evolution": f"{_database_uri}/evolution"
        
    }

    @staticmethod
    def get_database_uri(name: str):
        """Retorna a URI do banco de dados com base no nome fornecido."""
        name = name.lower()
        if name not in PostgresDatabases._databases:
            raise ValueError(f"Banco de dados '{name}' não encontrado. Escolha entre: {list(PostgresDatabases._databases.keys())}")
        return PostgresDatabases._databases[name]

    @staticmethod
    def __getitem__(name: str):
        """Permite acessar o banco de dados como se fosse um dicionário."""
        return PostgresDatabases.get_database_uri(name)

    # Propriedades estáticas para acesso direto
    ECOMMERCE = _databases["ecommerce"]
    CLINICA = _databases["clinica"]
    EVOLUTION = _databases["evolution"]

# Exemplo de uso
if __name__ == "__main__":
    try:
        print(PostgresDatabases.ECOMMERCE)  # Acesso direto
        print(PostgresDatabases["clinica"])  # Acesso via string
        print(PostgresDatabases.get_database_uri("evolution"))  # Acesso via método
    except ValueError as e:
        print(f"Erro: {e}")
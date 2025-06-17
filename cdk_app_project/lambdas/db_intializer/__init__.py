from .mysql_handler import MySQLHandler
from .postgres_handler import PostgresHandler
from .oracle_handler import OracleHandler
from .base_handler import DatabaseInitializationError

def get_db_handler(engine: str, secret_arn: str, endpoint: str, db_name: str):
    if engine == "mysql":
        return MySQLHandler(secret_arn, endpoint, db_name)
    elif engine == "postgres":
        return PostgresHandler(secret_arn, endpoint, db_name)
    elif engine == "oracle":
        return OracleHandler(secret_arn, endpoint, db_name)
    else:
        raise DatabaseInitializationError(f"Unsupported database engine: {engine}")

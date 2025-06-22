from abc import ABC, abstractmethod

class DatabaseInitializationError(Exception):
    pass

class BaseDBHandler(ABC):

    def __init__(self, secret_arn: str, endpoint: str, db_name: str):
        self.secret_arn = secret_arn
        self.endpoint = endpoint
        self.db_name = db_name

    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def execute_sql_script(self, conn, script_path: str):
        pass

    @abstractmethod
    def close_connection(self, conn):
        pass

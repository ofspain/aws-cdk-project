import json, boto3
import mysql.connector
from mysql.connector import errorcode
from .base_handler import BaseDBHandler, DatabaseInitializationError
from time import sleep

class MySQLHandler(BaseDBHandler):

    def get_connection(self):
        secrets = boto3.client('secretsmanager')
        creds = json.loads(secrets.get_secret_value(SecretId=self.secret_arn)['SecretString'])

        max_attempts, attempt, wait = 5, 0, 5
        while attempt < max_attempts:
            try:
                return mysql.connector.connect(
                    host=self.endpoint,
                    user=creds['username'],
                    password=creds['password'],
                    database=self.db_name,
                    connection_timeout=10,
                    connect_timeout=10,
                    autocommit=False
                )
            except mysql.connector.Error as err:
                if err.errno == errorcode.CR_CONN_HOST_ERROR:
                    sleep(wait)
                    wait *= 2
                    attempt += 1
                else:
                    raise DatabaseInitializationError(f"MySQL connection failed: {err}")
        raise DatabaseInitializationError("Max retries exceeded for MySQL connection")

    def execute_sql_script(self, conn, script_path: str):
        cursor = conn.cursor()
        with open(script_path, "r") as f:
            statements = [s.strip() for s in f.read().split(';') if s.strip()]
        try:
            for stmt in statements:
                cursor.execute(stmt)
            conn.commit()
        except mysql.connector.Error as err:
            conn.rollback()
            raise DatabaseInitializationError(f"MySQL error: {err}")
        finally:
            cursor.close()

    def close_connection(self, conn):
        if conn.is_connected():
            conn.close()

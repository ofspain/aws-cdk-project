import json, boto3, psycopg2
from .base_handler import BaseDBHandler, DatabaseInitializationError

class PostgresHandler(BaseDBHandler):

    def get_connection(self):
        secrets = boto3.client('secretsmanager')
        creds = json.loads(secrets.get_secret_value(SecretId=self.secret_arn)['SecretString'])

        try:
            return psycopg2.connect(
                host=self.endpoint,
                dbname=self.db_name,
                user=creds['username'],
                password=creds['password'],
                connect_timeout=10
            )
        except psycopg2.Error as err:
            raise DatabaseInitializationError(f"PostgreSQL connection failed: {err}")

    def execute_sql_script(self, conn, script_path: str):
        with conn.cursor() as cur, open(script_path, "r") as f:
            try:
                cur.execute(f.read())
                conn.commit()
            except Exception as err:
                conn.rollback()
                raise DatabaseInitializationError(f"PostgreSQL error: {err}")

    def close_connection(self, conn):
        if conn:
            conn.close()

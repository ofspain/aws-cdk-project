import json, boto3
import cx_Oracle
from .base_handler import BaseDBHandler, DatabaseInitializationError

class OracleHandler(BaseDBHandler):

    def get_connection(self):
        secrets = boto3.client('secretsmanager')
        creds = json.loads(secrets.get_secret_value(SecretId=self.secret_arn)['SecretString'])

        dsn = cx_Oracle.makedsn(self.endpoint, 1521, service_name=self.db_name)
        try:
            return cx_Oracle.connect(
                user=creds['username'],
                password=creds['password'],
                dsn=dsn,
                encoding="UTF-8"
            )
        except cx_Oracle.Error as err:
            raise DatabaseInitializationError(f"Oracle connection failed: {err}")

    def execute_sql_script(self, conn, script_path: str):
        with conn.cursor() as cursor, open(script_path, "r") as f:
            for statement in f.read().split(';'):
                stmt = statement.strip()
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        conn.rollback()
                        raise DatabaseInitializationError(f"Oracle error: {e}")
            conn.commit()

    def close_connection(self, conn):
        conn.close()

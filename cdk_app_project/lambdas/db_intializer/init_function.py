import os
import json
import logging
from turtledemo.sorting_animate import init_shelf
from typing import Dict, Any

from aws_lambda_powertools import Logger

from cdk_app_project.lambdas.db_intializer import get_db_handler, DatabaseInitializationError


logger = Logger(service="db-initializer", level=os.getenv("LOG_LEVEL", "INFO"))

@logger.inject_lambda_context(log_event=True)
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    request_type = event.get("RequestType", "Create")
    logger.info(f"Received event type: {request_type}")

    try:
        required_vars = ["DB_SECRET_ARN", "DB_ENDPOINT", "DB_NAME", "DB_ENGINE"]
        for var in required_vars:
            if var not in os.environ:
                raise DatabaseInitializationError(f"Missing required environment variable: {var}")

        secret_arn = os.environ["DB_SECRET_ARN"]
        endpoint = os.environ["DB_ENDPOINT"]
        db_name = os.environ["DB_NAME"]
        db_engine = os.environ["DB_ENGINE"].lower()  # e.g. mysql, postgres, oracle

        init_handler = get_db_handler(db_engine, secret_arn, endpoint, db_name)

        logger.info(f"Initializing {db_engine} database at {endpoint}")
        conn = init_handler.get_connection()

        try:
            init_handler.execute_sql_script(conn, "scripts/script.sql")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"{db_engine.capitalize()} database initialized successfully",
                    "database": db_name
                })
            }
        finally:
            init_handler.close_connection(conn)

    except DatabaseInitializationError as e:
        logger.error(f"Initialization error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Unexpected error", "error": str(e)})
        }

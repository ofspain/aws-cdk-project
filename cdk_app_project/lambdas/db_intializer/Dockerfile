FROM public.ecr.aws/lambda/python:3.12

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY __init__.py ${LAMBDA_TASK_ROOT}
COPY base_handler.py ${LAMBDA_TASK_ROOT}
COPY init_function.py ${LAMBDA_TASK_ROOT}
COPY mysql_handler.py ${LAMBDA_TASK_ROOT}
COPY oracle_handler.py ${LAMBDA_TASK_ROOT}
COPY postgres_handler.py ${LAMBDA_TASK_ROOT}

# Copy scripts and data explicitly
COPY scripts/ ${LAMBDA_TASK_ROOT}/scripts/
# COPY data/ ${LAMBDA_TASK_ROOT}/data/

# Set handler
CMD ["init_function.handler"]

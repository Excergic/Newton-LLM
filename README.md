# Newton-LLM: AI Version of Issac Newton  

## Live App  
https://newton-llm-48ychkz8x5fbutyhbfwdhb.streamlit.app/


## 1. Data Ingestion  
### - Airlfow Setup using UV  
```bash
pip install uv 
     #or 
brew install uv

uv init
uv venv
souce venv/bin/activate 
```
```bash
# Airflow Setup
AIRFLOW_VERSION=3.0.6

# Extract the version of Python you have installed. If you're currently using a Python version that is not supported by Airflow, you may want to set this manually.
# See above for supported versions.
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example this would install 3.0.0 with python 3.9: https://raw.githubusercontent.com/apache/airflow/constraints-3.0.6/constraints-3.9.txt

uv pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```
```bash
# Run Apache Airflow
airflow standalone
```

### Up MongoDB service with Docker
```bash
docker compose up -d
```

### Run DAG
- Go to airflow ui and run DAG manually to test, it will take a while to run, it will fetch data from Wikipedia and store it in MongoDB

## RAG (Retrieval Augmented Generation)
- There are several files in RAG which contails different components of RAG pipeline as a module  

![system design](https://raw.githubusercontent.com/Excergic/Newton-LLM/main/media/system.png)



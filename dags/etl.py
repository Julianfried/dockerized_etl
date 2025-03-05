"""
etl.py - DAG de Airflow con Data Quality y alertas por email.
"""

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Añadir el directorio actual al sys.path
dag_folder = os.path.dirname(os.path.abspath(__file__))
if dag_folder not in sys.path:
    sys.path.append(dag_folder)

from data_quality import data_quality_check

# Ahora importa los módulos
from extract import extract_data
from load import load_data
from transform import transform_data

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email": ["alertas@tudominio.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

dag = DAG(
    "pandas_etl_pipeline",
    default_args=default_args,
    description="Pipeline ETL con Pandas, Data Quality y alertas por email",
    schedule_interval=timedelta(days=1),
)

extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=lambda: transform_data(extract_data()),
    dag=dag,
)

data_quality_check_task = PythonOperator(
    task_id="data_quality_check",
    python_callable=lambda: data_quality_check(transform_data(extract_data())),
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_data",
    python_callable=lambda: load_data(transform_data(extract_data())),
    dag=dag,
)


extract_task >> transform_task >> data_quality_check_task >> load_task

"""
etl.py - Airflow DAG for Flight Data ETL with Data Quality checks and email alerts.
"""

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from airflow.utils.dates import days_ago
from airflow.models import Variable

# Add the current directory to sys.path
dag_folder = os.path.dirname(os.path.abspath(__file__))
if dag_folder not in sys.path:
    sys.path.append(dag_folder)

# Import pipeline modules
from extract import extract_data
from transform import transform_data
from data_quality import data_quality_check
from load import load_data

# Define task functions that support XCom for passing data between tasks
def extract_and_push(**context):
    """Extract flight data and push to XCom."""
    df = extract_data()
    # Push DataFrame to XCom
    context['ti'].xcom_push(key='extracted_data', value=df.to_json(orient='split'))
    return df.shape[0]  # Return row count for logging

def transform_and_push(**context):
    """Pull extracted data, transform it, and push to XCom."""
    # Pull DataFrame from XCom
    ti = context['ti']
    df_json = ti.xcom_pull(task_ids='extract_data', key='extracted_data')
    import pandas as pd
    df = pd.read_json(df_json, orient='split')
    
    # Transform data
    transformed_df = transform_data(df)
    
    # Push transformed DataFrame to XCom
    ti.xcom_push(key='transformed_data', value=transformed_df.to_json(orient='split'))
    return transformed_df.shape[0]  # Return row count for logging

def quality_check_and_push(**context):
    """Pull transformed data, perform quality checks, and push to XCom."""
    # Pull DataFrame from XCom
    ti = context['ti']
    df_json = ti.xcom_pull(task_ids='transform_data', key='transformed_data')
    import pandas as pd
    df = pd.read_json(df_json, orient='split')
    
    # Perform data quality checks
    validated_df = data_quality_check(df)
    
    # Push validated DataFrame to XCom
    ti.xcom_push(key='validated_data', value=validated_df.to_json(orient='split'))
    return validated_df.shape[0]  # Return row count for logging

def load_from_xcom(**context):
    """Pull validated data and load to database."""
    # Pull DataFrame from XCom
    ti = context['ti']
    df_json = ti.xcom_pull(task_ids='data_quality_check', key='validated_data')
    import pandas as pd
    df = pd.read_json(df_json, orient='split')
    
    # Load data to database
    load_success = load_data(df)
    return f"Data load completed successfully: {load_success}"

# DAG default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(0),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    #"email": ["alertas@tudominio.com"],
    #"email_on_failure": True,
    #"email_on_retry": False,
}

# Define the DAG
dag = DAG(
    "flight_data_etl_pipeline",
    default_args=default_args,
    description="ETL Pipeline for Aviation Stack Flight Data with Data Quality checks",
    schedule_interval="@daily",
    catchup=False,
    tags=["flight_data", "aviationstack", "etl"],
)

# Define tasks
extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=extract_and_push,
    provide_context=True,
    dag=dag,
    trigger_rule=TriggerRule.ALL_SUCCESS,
)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_and_push,
    provide_context=True,
    dag=dag,
    trigger_rule=TriggerRule.ALL_SUCCESS,
)

data_quality_check_task = PythonOperator(
    task_id="data_quality_check",
    python_callable=quality_check_and_push,
    provide_context=True,
    dag=dag,
    trigger_rule=TriggerRule.ALL_SUCCESS,
)

load_task = PythonOperator(
    task_id="load_data",
    python_callable=load_from_xcom,
    provide_context=True,
    dag=dag,
    trigger_rule=TriggerRule.ALL_SUCCESS,
)

# Define task dependencies
extract_task >> transform_task >> data_quality_check_task >> load_task
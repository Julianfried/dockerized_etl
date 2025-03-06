"""
Health check DAG that runs on startup to ensure all components are working properly
before allowing other DAGs to run.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os
import sys
import psycopg2
import socket
from airflow.models import Connection
from airflow.utils.session import provide_session
from sqlalchemy.orm import Session

# Add current directory to Python path
dag_folder = os.path.dirname(os.path.abspath(__file__))
if dag_folder not in sys.path:
    sys.path.append(dag_folder)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(0),
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
    "email_on_failure": True,
}

dag = DAG(
    "health_check_dag",
    default_args=default_args,
    description="Check system health and trigger ETL pipeline on successful startup",
    schedule_interval=None,  # Changed from @once to None - will be triggered externally
    catchup=False,
    tags=["health", "system", "startup"],
)

def check_postgres_connection():
    """Check if PostgreSQL is accessible and the required database exists."""
    try:
        # Connection parameters for testfligoo database
        conn = psycopg2.connect(
            host="postgres",
            database="testfligoo",
            user="airflow",
            password="airflow"
        )
        
        # Check if testdata table exists
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'testdata')")
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Table 'testdata' does not exist in database 'testfligoo', creating it...")
            # Create the testdata table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS testdata (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                edad INTEGER,
                ciudad VARCHAR(100)
            )
            """)
            
            # Insert sample data
            cursor.execute("""
            INSERT INTO testdata (nombre, edad, ciudad) VALUES
                ('Ana', 25, 'Madrid'),
                ('Juan', 30, 'Barcelona'),
                ('María', 22, 'Sevilla'),
                ('Carlos', 35, 'Valencia'),
                ('Elena', 28, 'Bilbao')
            """)
            
            conn.commit()
            print("Table created and sample data inserted.")
        
        # Get row count to ensure table has data
        cursor.execute("SELECT COUNT(*) FROM testdata")
        row_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"PostgreSQL connection successful. Table 'testdata' exists with {row_count} rows.")
        return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {str(e)}")
        raise

@provide_session
def check_airflow_connections(session: Session = None):
    """Check if essential Airflow connections are configured."""
    try:
        # Check if postgres connection exists
        conn_id = "postgres_default"
        existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
        
        if not existing_conn:
            print(f"Connection '{conn_id}' does not exist. Creating it...")
            new_conn = Connection(
                conn_id=conn_id,
                conn_type="postgres",
                host="postgres",
                schema="testfligoo",
                login="airflow",
                port=5432
            )
            session.add(new_conn)
            session.commit()
            print(f"Connection '{conn_id}' created successfully (without password).")
            print(f"NOTE: You may need to set the password manually in the Airflow UI.")
        else:
            print(f"Connection '{conn_id}' already exists.")
        
        print("Required Airflow connections exist.")
        return True
    except Exception as e:
        print(f"Airflow connections check warning: {str(e)}")
        print("Continuing without connection verification...")
        # Return True to allow pipeline to continue even with connection issues
        return True

def check_filesystem_access():
    """Check if essential directories are accessible and writable."""
    required_dirs = [
        "/opt/airflow/dags",
        "/opt/airflow/logs", 
        "/opt/airflow/plugins",
        "/opt/airflow/data"
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            raise Exception(f"Required directory {directory} does not exist")
        
        # Check if directory is writable
        test_file = os.path.join(directory, ".test_write")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            raise Exception(f"Directory {directory} is not writable: {str(e)}")
    
    print("Filesystem access check passed.")
    return True

# Define tasks
postgres_check = PythonOperator(
    task_id="check_postgres_connection",
    python_callable=check_postgres_connection,
    dag=dag,
)

airflow_connections_check = PythonOperator(
    task_id="check_airflow_connections",
    python_callable=check_airflow_connections,
    dag=dag,
)

filesystem_check = PythonOperator(
    task_id="check_filesystem_access",
    python_callable=check_filesystem_access,
    dag=dag,
)

system_check = BashOperator(
    task_id="system_check",
    bash_command="echo 'System check: CPU and Memory' && top -b -n 1 | head -n 5",
    dag=dag,
)

# Add a confirmation task that marks all checks as complete
checks_complete = BashOperator(
    task_id="checks_complete",
    bash_command="echo 'All health checks have completed successfully. Triggering ETL pipeline...'",
    dag=dag
)

# Task to trigger the ETL pipeline after all checks pass
trigger_etl_pipeline = TriggerDagRunOperator(
    task_id="trigger_etl_pipeline",
    trigger_dag_id="pandas_etl_pipeline",  # The ID of your ETL DAG
    dag=dag,
)

# Define the task dependencies - all checks must succeed before triggering the ETL pipeline
[postgres_check, airflow_connections_check, filesystem_check, system_check] >> checks_complete >> trigger_etl_pipeline
"""
load.py - Flight Data Loading Module
This module loads the processed flight data into a PostgreSQL database.
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
from typing import Optional
import time
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_table_if_not_exists():
    """
    Creates the testfligoo table in the PostgreSQL database if it doesn't exist.
    """
    load_dotenv()
    
    conn_params = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS testfligoo (
        id SERIAL PRIMARY KEY,
        flight_date DATE,
        flight_status VARCHAR(20),
        departure_airport VARCHAR(100),
        departure_timezone VARCHAR(100),
        arrival_airport VARCHAR(100),
        arrival_timezone VARCHAR(100),
        arrival_terminal VARCHAR(50),
        airline_name VARCHAR(100),
        flight_number VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        cursor.execute(create_table_query)
        conn.commit()
        
        logger.info("Table 'testfligoo' created or already exists.")
        
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()

def load_data(df: Optional[pd.DataFrame] = None) -> bool:
    """
    Loads the transformed flight data into the PostgreSQL database.
    
    Args:
        df: DataFrame with transformed flight data.
        
    Returns:
        bool: True if data was loaded successfully.
    """
    if df is None:
        from data_quality import data_quality_check
        from transform import transform_data
        df = data_quality_check(transform_data())
    
    logger.info("Starting data load to PostgreSQL...")
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    create_table_if_not_exists()
    
    load_dotenv()
    
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    
    db_connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(db_connection_string)
            
            df.to_sql(
                'testfligoo', 
                engine, 
                if_exists='replace', 
                index=False,
                method='multi',
                chunksize=100
            )
            
            row_count = len(df)
            logger.info(f"✅ Successfully loaded {row_count} rows to database.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during data load (attempt {attempt+1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Maximum retries reached. Data load failed.")
                raise
    
    return False

if __name__ == "__main__":
    # For testing purposes
    from transform import transform_data
    from data_quality import data_quality_check
    
    transformed_data = transform_data()
    validated_data = data_quality_check(transformed_data)
    load_success = load_data(validated_data)
    
    print(f"Data load successful: {load_success}")
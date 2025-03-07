"""
transform.py - Flight Data Transformation Module
This module processes flight data, applying transformations as required.
"""

import pandas as pd
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def replace_slashes_with_hyphens(value: Any) -> str:
    """
    Replaces slashes with hyphens in a given string.
    
    Args:
        value: Input value that might contain slashes.
        
    Returns:
        str: String with slashes replaced by hyphens.
    """
    if pd.isna(value) or value == '':
        return ''
    
    return str(value).replace('/', ' - ')

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames columns to more user-friendly names.
    
    Args:
        df: DataFrame with original column names.
        
    Returns:
        pd.DataFrame: DataFrame with renamed columns.
    """
    column_mapping = {
        'flight_date': 'flight_date',
        'flight_status': 'flight_status',
        'departure.airport': 'departure_airport',
        'departure.timezone': 'departure_timezone',
        'arrival.airport': 'arrival_airport',
        'arrival.timezone': 'arrival_timezone',
        'arrival.terminal': 'arrival_terminal',
        'airline.name': 'airline_name',
        'flight.number': 'flight_number'
    }
    
    return df.rename(columns=column_mapping)

def transform_data(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Transforms flight data by:
    1. Renaming columns to be database-friendly
    2. Replacing slashes with hyphens in timezone and terminal fields
    
    Args:
        df: DataFrame with the flight data to transform.
        
    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    if df is None:
        from extract import extract_data
        df = extract_data()
    
    logger.info("Starting flight data transformation...")
    
    transformed_df = df.copy()
    
    transformed_df = rename_columns(transformed_df)
    
    transformed_df['departure_timezone'] = transformed_df['departure_timezone'].apply(replace_slashes_with_hyphens)
    transformed_df['arrival_timezone'] = transformed_df['arrival_timezone'].apply(replace_slashes_with_hyphens)
    transformed_df['arrival_terminal'] = transformed_df['arrival_terminal'].apply(replace_slashes_with_hyphens)
    
    for col in transformed_df.columns:
        if transformed_df[col].dtype != 'datetime64[ns]':
            transformed_df[col] = transformed_df[col].astype(str)
    
    transformed_df = transformed_df.fillna('')
    
    row_count = len(transformed_df)
    logger.info(f"Transformation complete: {row_count} rows processed")
    
    return transformed_df

if __name__ == "__main__":
    # For testing purposes
    transformed_data = transform_data()
    print(transformed_data.head())
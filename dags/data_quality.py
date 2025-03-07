"""
data_quality.py - Data Quality Check Module with Great Expectations
This module implements data quality checks for flight data.
"""

import pandas as pd
import os
import logging
from typing import Optional
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get plugins directory path
dag_folder = os.path.dirname(os.path.abspath(__file__))
plugins_folder = os.path.join(os.path.dirname(dag_folder), "plugins")
if plugins_folder not in sys.path:
    sys.path.append(plugins_folder)

try:
    from great_expectations_utils import GreatExpectationsUtils
    GREAT_EXPECTATIONS_AVAILABLE = True
except ImportError:
    logger.warning("Great Expectations utils not available. Data quality checks will be skipped.")
    GREAT_EXPECTATIONS_AVAILABLE = False

def define_flight_data_expectations():
    """
    Define expectations for flight data validation.
    
    Returns:
        list: List of expectations for Great Expectations.
    """
    return [
        # Required columns should exist
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "flight_date"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "flight_status"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "departure_airport"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "departure_timezone"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "arrival_airport"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "arrival_timezone"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "arrival_terminal"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "airline_name"}},
        {"expectation": "expect_column_to_exist", "kwargs": {"column": "flight_number"}},
        
        # Flight status should be valid
        {"expectation": "expect_column_values_to_be_in_set", 
         "kwargs": {"column": "flight_status", "value_set": ["active", "scheduled", "landed", "cancelled", "diverted", "incident", "delayed"]}},
        
        # Timezone fields should have hyphens instead of slashes
        {"expectation": "expect_column_values_to_not_match_regex", 
         "kwargs": {"column": "departure_timezone", "regex": ".*\/.*"}},
        {"expectation": "expect_column_values_to_not_match_regex", 
         "kwargs": {"column": "arrival_timezone", "regex": ".*\/.*"}},
        
        # Terminal field should have hyphens instead of slashes
        {"expectation": "expect_column_values_to_not_match_regex", 
         "kwargs": {"column": "arrival_terminal", "regex": ".*\/.*"}},
    ]

def data_quality_check(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Performs data quality checks on flight data using Great Expectations.
    
    Args:
        df: DataFrame with flight data to validate.
        
    Returns:
        pd.DataFrame: Validated DataFrame.
    """
    if df is None:
        # For testing from other modules
        from transform import transform_data
        df = transform_data()
    
    logger.info("Starting data quality checks...")
    
    # If Great Expectations is not available, skip validation and return original DataFrame
    if not GREAT_EXPECTATIONS_AVAILABLE:
        logger.warning("⚠️ Great Expectations not available. Skipping data quality checks.")
        return df
    
    try:
        # Create data directory if it doesn't exist
        data_dir = "/opt/airflow/data/great_expectations"
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize Great Expectations utilities
        ge_utils = GreatExpectationsUtils(
            data_dir=data_dir, 
            suite_name="flight_data_suite"
        )
        
        # Define expectations
        expectations = define_flight_data_expectations()
        
        # Validate DataFrame against expectations
        validation_result = ge_utils.validate_dataframe(
            df=df,
            expectations=expectations,
            raise_on_failure=False  # Log errors but don't stop the pipeline
        )
        
        if validation_result:
            logger.info("✅ Data quality checks passed successfully.")
        else:
            logger.warning("⚠️ Some data quality checks failed, but pipeline will continue.")
        
        # Return the validated DataFrame
        return df
    
    except Exception as e:
        logger.error(f"Error during data quality checks: {str(e)}")
        # Return original DataFrame even if quality checks fail
        logger.warning("⚠️ Data quality check encountered errors, but pipeline will continue with original data.")
        return df

if __name__ == "__main__":
    # For testing purposes
    from transform import transform_data
    validated_data = data_quality_check(transform_data())
    print(validated_data.head())
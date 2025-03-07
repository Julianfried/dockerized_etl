"""
great_expectations_utils.py - Great Expectations Utilities
This module provides utilities for data quality validation using Great Expectations.
"""

import os
import logging
import pandas as pd
import great_expectations as gx
from typing import List, Dict, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GreatExpectationsUtils:
    """
    Utilities for data quality validation using Great Expectations.
    """
    
    def __init__(self, data_dir: str, suite_name: str = "default_suite"):
        """
        Initialize Great Expectations utilities.
        
        Args:
            data_dir: Directory for Great Expectations data
            suite_name: Name of the expectation suite
        """
        self.data_dir = data_dir
        self.suite_name = suite_name
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize context
        try:
            self.context = gx.get_context()
            logger.info("Great Expectations context initialized successfully.")
        except Exception as e:
            logger.warning(f"Error initializing Great Expectations context: {str(e)}")
            logger.info("Attempting to create a new context...")
            try:
                # Create a new ephemeral context if we can't load an existing one
                self.context = gx.get_context(
                    context_root_dir=data_dir,
                    enforce_metadata_restriction=False
                )
                logger.info("Created new Great Expectations context.")
            except Exception as e2:
                logger.error(f"Failed to create Great Expectations context: {str(e2)}")
                raise
    
    def validate_dataframe(
        self, 
        df: pd.DataFrame, 
        expectations: List[Dict[str, Any]],
        raise_on_failure: bool = True
    ) -> bool:
        """
        Validate a DataFrame against a list of expectations.
        
        Args:
            df: DataFrame to validate
            expectations: List of expectations in dictionary format
            raise_on_failure: Whether to raise an exception if validation fails
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        logger.info(f"Validating DataFrame with {len(expectations)} expectations")
        
        try:
            # Convert DataFrame to a GX DataFrame
            gx_df = gx.from_pandas(df)
            
            # Create expectation suite if it doesn't exist
            if not self.context.list_expectation_suite_names():
                logger.info(f"Creating new expectation suite: {self.suite_name}")
                expectation_suite = self.context.add_or_update_expectation_suite(
                    expectation_suite_name=self.suite_name
                )
            else:
                expectation_suite = self.context.get_expectation_suite(self.suite_name)
            
            # Apply each expectation from our list
            validation_results = []
            
            for expectation in expectations:
                expectation_type = expectation["expectation"]
                expectation_kwargs = expectation.get("kwargs", {})
                
                try:
                    # Get the expectation method and call it
                    if hasattr(gx_df, expectation_type):
                        expectation_method = getattr(gx_df, expectation_type)
                        result = expectation_method(**expectation_kwargs)
                        validation_results.append(result)
                        
                        # Log the result
                        success = result.success
                        expectation_str = f"{expectation_type}({', '.join([f'{k}={v}' for k, v in expectation_kwargs.items()])})"
                        
                        if success:
                            logger.info(f"✅ Passed: {expectation_str}")
                        else:
                            logger.warning(f"❌ Failed: {expectation_str}")
                            
                    else:
                        logger.warning(f"Expectation '{expectation_type}' is not a valid expectation method")
                        validation_results.append(False)
                        
                except Exception as e:
                    logger.error(f"Error applying expectation '{expectation_type}': {str(e)}")
                    validation_results.append(False)
            
            # Check if all validations passed
            all_passed = all(result.success if hasattr(result, 'success') else False for result in validation_results)
            
            if all_passed:
                logger.info("✅ All data quality validations passed!")
            else:
                logger.warning("❌ Some data quality validations failed.")
                if raise_on_failure:
                    raise ValueError("Data quality validation failed")
                    
            return all_passed
            
        except Exception as e:
            logger.error(f"Error during data validation: {str(e)}")
            if raise_on_failure:
                raise
            return False
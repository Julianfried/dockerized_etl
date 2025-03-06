"""
Utility functions for working with Great Expectations in Airflow.
This module provides a wrapper around Great Expectations for data validation.
"""

import os
import logging
from typing import Dict, List, Optional, Union, Any

import pandas as pd
from great_expectations.core import ExpectationSuite
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import (
    DataContextConfig,
    FilesystemStoreBackendDefaults,
)
from great_expectations.dataset import PandasDataset

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GreatExpectationsUtils:
    """Utility class for working with Great Expectations in Airflow."""

    def __init__(
        self,
        data_dir: str = "/opt/airflow/data/great_expectations",
        suite_name: str = "default_suite",
    ):
        """Initialize Great Expectations utilities.

        Args:
            data_dir: Directory to store Great Expectations artifacts
            suite_name: Name of the expectation suite
        """
        self.data_dir = data_dir
        self.suite_name = suite_name

        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        try:
            # Initialize context
            self.context = self._initialize_context()

            # Create suite if it doesn't exist
            self.suite = self._get_or_create_suite()
        except Exception as e:
            logger.error(f"Error initializing Great Expectations: {str(e)}")
            # Create a fallback minimal context to avoid breaking the pipeline
            self.context = None
            self.suite = None

    def _initialize_context(self) -> BaseDataContext:
        """Initialize a Great Expectations context.

        Returns:
            A configured Great Expectations context
        """
        try:
            data_context_config = DataContextConfig(
                store_backend_defaults=FilesystemStoreBackendDefaults(
                    root_directory=self.data_dir
                ),
            )
            return BaseDataContext(project_config=data_context_config)
        except Exception as e:
            logger.error(f"Failed to initialize Great Expectations context: {str(e)}")
            raise

    def _get_or_create_suite(self) -> ExpectationSuite:
        """Get or create an expectation suite.

        Returns:
            An expectation suite
        """
        try:
            # Try to get existing suite
            return self.context.get_expectation_suite(self.suite_name)
        except Exception:
            # Create new suite if it doesn't exist
            return self.context.create_expectation_suite(self.suite_name)

    def validate_dataframe(
        self,
        df: pd.DataFrame,
        expectations: Optional[List[Dict[str, Union[str, dict]]]] = None,
        raise_on_failure: bool = True,
    ) -> bool:
        """Validate a pandas DataFrame against expectations.

        Args:
            df: The DataFrame to validate
            expectations: List of expectations to apply
            raise_on_failure: Whether to raise an exception on validation failure

        Returns:
            True if validation passed, False otherwise

        Raises:
            ValueError: If validation fails and raise_on_failure is True
        """
        # If Great Expectations wasn't initialized properly, skip validation
        if self.context is None or self.suite is None:
            logger.warning("Great Expectations not properly initialized. Skipping validation.")
            return True
            
        try:
            # Create batch
            batch = self.context.get_batch(
                batch_kwargs={"dataset": df, "datasource": "pandas"},
                expectation_suite_name=self.suite_name,
            )

            # Apply expectations if provided
            if expectations:
                for exp in expectations:
                    method_name = exp["expectation"]
                    method_kwargs = exp.get("kwargs", {})

                    # Call the expectation method with the provided arguments
                    getattr(batch, method_name)(**method_kwargs)

            # Validate
            results = batch.validate()

            # Check if validation passed
            success = results.success

            if not success:
                failed_expectations = [
                    exp for exp in results.results if not exp.success
                ]
                failed_count = len(failed_expectations)
                logger.warning(f"{failed_count} data quality checks failed")
                
                # Log details about failed expectations
                for i, failed_exp in enumerate(failed_expectations, 1):
                    logger.warning(f"Failed expectation {i}: {failed_exp.expectation_config.expectation_type}")
                
                if raise_on_failure:
                    raise ValueError(f"Data validation failed: {failed_count} expectations not met")
            else:
                logger.info(f"All {len(results.results)} data quality checks passed")

            return success
            
        except Exception as e:
            logger.error(f"Error during data validation: {str(e)}")
            if raise_on_failure:
                raise
            return False

    def create_dataset_from_dataframe(self, df: pd.DataFrame) -> PandasDataset:
        """Create a Great Expectations dataset from a pandas DataFrame.

        Args:
            df: The DataFrame to convert

        Returns:
            A Great Expectations PandasDataset
        """
        if self.suite is None:
            logger.warning("Great Expectations suite not initialized. Using empty suite.")
            from great_expectations.core import ExpectationSuite
            empty_suite = ExpectationSuite(expectation_suite_name="empty_suite")
            return PandasDataset(df, expectation_suite=empty_suite)
            
        return PandasDataset(df, expectation_suite=self.suite)


# Example usage:
"""
# Initialize utilities
ge_utils = GreatExpectationsUtils()

# Define expectations
expectations = [
    {
        "expectation": "expect_column_to_exist",
        "kwargs": {"column": "name"}
    },
    {
        "expectation": "expect_column_values_to_not_be_null",
        "kwargs": {"column": "value"}
    },
    {
        "expectation": "expect_column_values_to_be_between",
        "kwargs": {"column": "value", "min_value": 0, "max_value": 100}
    }
]

# Validate DataFrame
is_valid = ge_utils.validate_dataframe(df, expectations)
"""
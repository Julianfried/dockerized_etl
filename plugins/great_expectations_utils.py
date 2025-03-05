"""Utility functions for working with Great Expectations in Airflow."""

import os
from typing import Dict, List, Optional, Union

import pandas as pd
from great_expectations.core import ExpectationSuite
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import (
    DataContextConfig,
    FilesystemStoreBackendDefaults,
)
from great_expectations.dataset import PandasDataset


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

        # Initialize context
        self.context = self._initialize_context()

        # Create suite if it doesn't exist
        self.suite = self._get_or_create_suite()

    def _initialize_context(self) -> BaseDataContext:
        """Initialize a Great Expectations context.

        Returns:
            A configured Great Expectations context
        """
        data_context_config = DataContextConfig(
            store_backend_defaults=FilesystemStoreBackendDefaults(
                root_directory=self.data_dir
            ),
        )
        return BaseDataContext(project_config=data_context_config)

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

        if not success and raise_on_failure:
            raise ValueError(f"Data validation failed: {results}")

        return success

    def create_dataset_from_dataframe(self, df: pd.DataFrame) -> PandasDataset:
        """Create a Great Expectations dataset from a pandas DataFrame.

        Args:
            df: The DataFrame to convert

        Returns:
            A Great Expectations PandasDataset
        """
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

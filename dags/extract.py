"""
extract.py - Flight Data Extraction Module
This module extracts real-time flight data from the AviationStack API.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
import logging


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_data() -> pd.DataFrame:
    """
    Extracts flight data from the AviationStack API.
    
    Returns:
        pd.DataFrame: DataFrame with the extracted flight data.
    """
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment variables
    api_key = os.getenv('API_KEY')
    if not api_key:
        error_msg = "AviationStack API key not found in environment variables."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Starting flight data extraction from AviationStack API...")
    
    # API endpoint for real-time flights
    url = "http://api.aviationstack.com/v1/flights"
    
    # Query parameters
    params = {
        'access_key': api_key,
        'flight_status': 'active',
        'limit': 100
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse JSON response
        data = response.json()
        
        if 'data' not in data:
            logger.error(f"Unexpected API response format: {data}")
            raise ValueError("Unexpected API response format - 'data' field missing")
        
        # Convert to DataFrame
        flights_df = pd.json_normalize(data['data'])
        
        # Filter only the required fields
        required_fields = [
            'flight_date', 
            'flight_status',
            'departure.airport',
            'departure.timezone',
            'arrival.airport',
            'arrival.timezone',
            'arrival.terminal',
            'airline.name',
            'flight.number'
        ]
        
        # Check if all required fields exist in the response
        for field in required_fields:
            if field not in flights_df.columns:
                # Use empty strings for missing fields to avoid errors
                base_field = field.split('.')[0]
                sub_field = field.split('.')[1] if '.' in field else None
                
                if sub_field and base_field in flights_df.columns:
                    flights_df[field] = ""
                else:
                    flights_df[field] = ""
        
        # Select only the required fields
        flights_df = flights_df[required_fields]
        
        # Handle potential NaN values
        flights_df = flights_df.fillna('')
        
        logger.info(f"Successfully extracted {len(flights_df)} flight records")
        return flights_df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during data extraction: {str(e)}")
        raise

if __name__ == "__main__":
    # For testing purposes
    df = extract_data()
    print(df.head())
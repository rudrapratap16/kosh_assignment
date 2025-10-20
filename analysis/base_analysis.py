import pandas as pd
from abc import ABC, abstractmethod

class BaseAnalysis(ABC):
    """Abstract base class for water quality analysis"""
    
    def __init__(self, station_name: str):
        self.station_name = station_name
    
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw data and return analyzed DataFrame
        
        Args:
            df: Raw input DataFrame
        
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        pass
    
    def validate_input(self, df: pd.DataFrame, required_columns: list) -> bool:
        """
        Validate that DataFrame has required columns
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
        
        Returns:
            bool: True if valid
        """
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        return True
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Common data cleaning operations
        
        Args:
            df: DataFrame to clean
        
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.dropna(how='all')
        
        # Convert date column if exists
        if 'Dates' in df.columns:
            df['Dates'] = pd.to_datetime(df['Dates'], errors='coerce')
        
        return df
    
    def get_numeric_columns(self, df: pd.DataFrame) -> list:
        """
        Get list of numeric columns excluding date columns
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            list: Numeric column names
        """
        return [
            col for col in df.columns 
            if pd.api.types.is_numeric_dtype(df[col]) 
            and col.lower() not in ['date', 'dates']
        ]
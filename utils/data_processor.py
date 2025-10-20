import pandas as pd
import streamlit as st
from typing import Tuple, Optional

class DataProcessor:
    """Class to handle data processing operations"""
    
    @staticmethod
    def read_file(uploaded_file) -> Optional[pd.DataFrame]:
        """
        Read uploaded file (Excel or CSV)
        
        Args:
            uploaded_file: Streamlit uploaded file object
        
        Returns:
            pd.DataFrame or None: Loaded DataFrame or None if error
        """
        try:
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload Excel or CSV file.")
                return None
            
            return df
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None
    
    @staticmethod
    def get_numeric_columns(df: pd.DataFrame, exclude_cols: list = None) -> list:
        """
        Get numeric columns from DataFrame
        
        Args:
            df: DataFrame to analyze
            exclude_cols: List of column names to exclude
        
        Returns:
            list: Numeric column names
        """
        if exclude_cols is None:
            exclude_cols = ['date', 'dates']
        
        return [
            col for col in df.columns 
            if pd.api.types.is_numeric_dtype(df[col]) 
            and col.lower() not in [e.lower() for e in exclude_cols]
        ]
    
    @staticmethod
    def get_date_column(df: pd.DataFrame) -> Optional[str]:
        """
        Find date column in DataFrame
        
        Args:
            df: DataFrame to search
        
        Returns:
            str or None: Date column name or None if not found
        """
        date_cols = ['Dates', 'Date', 'dates', 'date', 'DATE']
        for col in date_cols:
            if col in df.columns:
                return col
        return None
    
    @staticmethod
    def prepare_for_download(df: pd.DataFrame, file_format: str = "csv") -> bytes:
        """
        Prepare DataFrame for download
        
        Args:
            df: DataFrame to prepare
            file_format: Format ('csv' or 'excel')
        
        Returns:
            bytes: Encoded file data
        """
        if file_format == "csv":
            return df.to_csv(index=False).encode('utf-8')
        elif file_format == "excel":
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()
    
    @staticmethod
    def calculate_statistics(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """
        Calculate statistics for specified columns
        
        Args:
            df: DataFrame containing data
            columns: List of columns to analyze
        
        Returns:
            pd.DataFrame: Statistics summary
        """
        return df[columns].describe()
    
    @staticmethod
    def filter_by_date_range(df: pd.DataFrame, start_date, end_date, 
                            date_column: str = 'Dates') -> pd.DataFrame:
        """
        Filter DataFrame by date range
        
        Args:
            df: DataFrame to filter
            start_date: Start date
            end_date: End date
            date_column: Name of date column
        
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        mask = (df[date_column].dt.date >= start_date) & (df[date_column].dt.date <= end_date)
        return df[mask]
import pandas as pd
import numpy as np
from analysis.base_analysis import BaseAnalysis

class TUSAnalysis(BaseAnalysis):
    """TUS Station water quality analysis"""
    
    # Define parameter order for TUS station
    PARAM_ORDER = [
        'FLOW, IN', 'BOD, IN', 'TSS, IN', 'TEMP, IN', 'PH, IN',
        'FLOW, EFF', 'BOD, EFF', 'TSS, EFF', 'TEMP, EFF', 'PH, EFF',
        'DO, IN', 'DO, EFF', 'FC, EFF', 'NH4, EFF', 'TN, EFF', 'TP, EFF',
        'FC, IN', 'BOD CALC', 'BOD, REM', 'TSS, REM', 'BOD, L', 'TSS, L', 
        'NH4, L', 'TN, L', 'TP, L'
    ]
    
    REQUIRED_COLUMNS = ['Station_ID', 'Date_Time', 'PCode', 'Result']
    
    def __init__(self):
        super().__init__(station_name="TUS")
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process TUS station raw data
        
        Args:
            df: Raw input DataFrame with columns: Station_ID, Date_Time, PCode, Result
        
        Returns:
            pd.DataFrame: Processed TUS analysis data with pivoted structure
        """
        # Validate input
        self.validate_input(df, self.REQUIRED_COLUMNS)
        
        # Filter for TUS station
        df = df[df['Station_ID'] == 'TUS'].copy()
        
        if df.empty:
            raise ValueError("No data found for TUS station")
        
        # Clean and prepare data
        df = self._clean_raw_data(df)
        
        # Pivot data
        output_df = self._pivot_data(df)
        
        return output_df
    
    def _clean_raw_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean raw data before pivoting
        
        Args:
            df: Raw DataFrame
        
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        df = df.copy()
        
        # Strip whitespace from column names and string columns
        df.columns = df.columns.str.strip()
        df['PCode'] = df['PCode'].str.strip()
        
        # Convert Date_Time to date
        df['Date'] = pd.to_datetime(df['Date_Time']).dt.date
        
        return df
    
    def _pivot_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pivot data from long format to wide format
        
        Args:
            df: Cleaned DataFrame in long format
        
        Returns:
            pd.DataFrame: Pivoted DataFrame with Data 1-25 columns
        """
        result_rows = []
        
        # Get unique station-date combinations
        unique_dates = df.groupby(['Station_ID', 'Date']).size().reset_index()[['Station_ID', 'Date']]
        
        for _, row in unique_dates.iterrows():
            station = row['Station_ID']
            date = row['Date']
            
            # Filter data for this station and date
            date_data = df[(df['Station_ID'] == station) & (df['Date'] == date)]
            
            # Initialize row with station and date
            result_row = {
                'Station': station, 
                'Dates': str(date)
            }
            
            # Initialize all Data columns as NaN
            for i in range(1, 26):
                result_row[f'Data {i}'] = np.nan
            
            # Fill values based on PCode position
            for _, record in date_data.iterrows():
                pcode = record['PCode']
                if pcode in self.PARAM_ORDER:
                    col_idx = self.PARAM_ORDER.index(pcode) + 1
                    result_row[f'Data {col_idx}'] = record['Result']
            
            result_rows.append(result_row)
        
        # Create output dataframe
        output_df = pd.DataFrame(result_rows)
        
        # Format dates and sort
        output_df['Dates'] = pd.to_datetime(output_df['Dates'])
        output_df = output_df.sort_values(['Station', 'Dates'])
        output_df['Dates'] = output_df['Dates'].dt.strftime('%Y-%m-%d')
        
        # Reorder columns
        cols = ['Station', 'Dates'] + [f'Data {i}' for i in range(1, 26)]
        output_df = output_df[cols]
        
        return output_df
    
    def get_parameter_mapping(self) -> dict:
        """
        Get mapping of Data columns to parameter names
        
        Returns:
            dict: Mapping of column names to parameters
        """
        return {f'Data {i+1}': param for i, param in enumerate(self.PARAM_ORDER)}


def run_tus_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wrapper function for backward compatibility
    
    Args:
        df: Raw input DataFrame
    
    Returns:
        pd.DataFrame: Processed TUS data
    """
    analyzer = TUSAnalysis()
    return analyzer.process(df)
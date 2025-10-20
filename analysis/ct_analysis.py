import pandas as pd
import numpy as np
from analysis.base_analysis import BaseAnalysis

class CTAnalysis(BaseAnalysis):
    """CT Station water quality analysis"""
    
    # Define parameter order for CT station
    PARAM_ORDER = [
        'FLOW, IN', 'BOD, IN', 'TSS, IN', 'TEMP, IN', 'PH, IN',
        'FLOW, EFF', 'BOD, EFF', 'TSS, EFF', 'TEMP, EFF', 'PH, EFF',
        'DO, IN', 'DO, EFF', 'FC, EFF', 'NH4, EFF', 'TN, EFF', 'TP, EFF',
        'FC, IN', 'BOD CALC', 'BOD, REM', 'TSS, REM', 'BOD, L', 'TSS, L', 
        'NH4, L', 'TN, L', 'TP, L'
    ]
    
    REQUIRED_COLUMNS = ['Station_ID', 'Date_Time', 'PCode', 'Result']
    
    def __init__(self):
        super().__init__(station_name="CT")
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process CT station raw data
        
        Args:
            df: Raw input DataFrame with columns: Station_ID, Date_Time, PCode, Result
        
        Returns:
            pd.DataFrame: Processed CT analysis data with pivoted structure
        """
        # Validate input
        self.validate_input(df, self.REQUIRED_COLUMNS)
        
        # Filter for CT station
        df = df[df['Station_ID'] == 'CT'].copy()
        
        if df.empty:
            raise ValueError("No data found for CT station")
        
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
        
        # Group by station and date
        for (station, date), group in df.groupby(['Station_ID', 'Date']):
            row = {
                'Station': station, 
                'Dates': str(date)
            }
            
            # Initialize all Data columns
            for i in range(1, 26):
                row[f'Data {i}'] = np.nan
            
            # Fill values based on PCode position
            for _, record in group.iterrows():
                pcode = record['PCode']
                if pcode in self.PARAM_ORDER:
                    col_idx = self.PARAM_ORDER.index(pcode) + 1
                    row[f'Data {col_idx}'] = record['Result']
            
            result_rows.append(row)
        
        # Create output dataframe
        output_df = pd.DataFrame(result_rows)
        
        # Format dates and sort
        output_df['Dates'] = pd.to_datetime(output_df['Dates'])
        output_df = output_df.sort_values('Dates')
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


def run_ct_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wrapper function for backward compatibility
    
    Args:
        df: Raw input DataFrame
    
    Returns:
        pd.DataFrame: Processed CT data
    """
    analyzer = CTAnalysis()
    return analyzer.process(df)
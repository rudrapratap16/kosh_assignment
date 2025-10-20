import streamlit as st
import pandas as pd
from google.cloud import bigquery
from typing import Optional
from config.settings import settings

class BigQueryClient:
    """Class to handle all BigQuery operations"""
    
    def __init__(self):
        self.client = bigquery.Client()
        self.config = settings.bigquery
    
    def upload_dataframe(self, df: pd.DataFrame, table_id: str) -> bool:
        """
        Upload a dataframe to BigQuery
        
        Args:
            df: DataFrame to upload
            table_id: Full table ID (project.dataset.table)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_TRUNCATE"
            )
            job = self.client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()  # Wait for job to complete
            return True
        except Exception as e:
            st.error(f"Error uploading to BigQuery: {str(e)}")
            return False
    
    @st.cache_data(ttl=settings.app.cache_ttl)
    def query(_self, sql_query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        
        Args:
            sql_query: SQL query string
        
        Returns:
            pd.DataFrame: Query results
        """
        try:
            query_job = _self.client.query(sql_query)
            df = query_job.result().to_dataframe()
            
            # Convert Dates column to datetime if it exists
            if 'Dates' in df.columns:
                df['Dates'] = pd.to_datetime(df['Dates'])
            
            return df
        except Exception as e:
            st.error(f"Error querying BigQuery: {str(e)}")
            return pd.DataFrame()
    
    def get_table_columns(self, table_id: str) -> list:
        """
        Get column names from a BigQuery table
        
        Args:
            table_id: Full table ID
        
        Returns:
            list: Column names
        """
        try:
            table = self.client.get_table(table_id)
            return [field.name for field in table.schema]
        except Exception as e:
            st.error(f"Error getting table schema: {str(e)}")
            return []
    
    def table_exists(self, table_id: str) -> bool:
        """
        Check if a table exists in BigQuery
        
        Args:
            table_id: Full table ID
        
        Returns:
            bool: True if table exists
        """
        try:
            self.client.get_table(table_id)
            return True
        except Exception:
            return False
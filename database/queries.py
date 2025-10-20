from datetime import date

class QueryBuilder:
    """Class to build SQL queries for water quality data"""
    
    @staticmethod
    def get_filtered_data(table_id: str, start_date: date, end_date: date) -> str:
        """
        Build query to get filtered data by date range
        
        Args:
            table_id: Full table ID
            start_date: Start date for filter
            end_date: End date for filter
        
        Returns:
            str: SQL query
        """
        return f"""
        SELECT *
        FROM `{table_id}`
        WHERE DATE(Dates) BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY Dates
        """
    
    @staticmethod
    def get_date_range(table_id: str) -> str:
        """
        Get min and max dates from table
        
        Args:
            table_id: Full table ID
        
        Returns:
            str: SQL query
        """
        return f"""
        SELECT 
            MIN(DATE(Dates)) as min_date,
            MAX(DATE(Dates)) as max_date
        FROM `{table_id}`
        """
    
    @staticmethod
    def get_column_stats(table_id: str, column_name: str) -> str:
        """
        Get statistics for a specific column
        
        Args:
            table_id: Full table ID
            column_name: Column to analyze
        
        Returns:
            str: SQL query
        """
        return f"""
        SELECT 
            COUNT({column_name}) as count,
            AVG({column_name}) as avg,
            MIN({column_name}) as min,
            MAX({column_name}) as max,
            STDDEV({column_name}) as stddev
        FROM `{table_id}`
        WHERE {column_name} IS NOT NULL
        """
import streamlit as st
import pandas as pd
from typing import List, Tuple, Optional
from datetime import datetime, date

class Sidebar:
    """Class to manage sidebar components"""
    
    @staticmethod
    def render_upload_section(uploaded: bool) -> Optional[object]:
        """
        Render file upload section
        
        Args:
            uploaded: Whether file is already uploaded
        
        Returns:
            Uploaded file object or None
        """
        st.sidebar.header("📤 Data Upload")
        
        if not uploaded:
            uploaded_file = st.sidebar.file_uploader(
                "Upload Raw Data Excel/CSV", 
                type=["xlsx", "csv"]
            )
            return uploaded_file
        else:
            st.sidebar.success("✅ Data uploaded!")
            if st.sidebar.button("🔄 Upload New File"):
                return "RESET"
        return None
    
    @staticmethod
    def render_filters(stations: List[str]) -> Tuple[str, date, date]:
        """
        Render filter controls
        
        Args:
            stations: List of available stations
        
        Returns:
            Tuple of (station, start_date, end_date)
        """
        st.sidebar.header("🔍 Filters")
        
        station = st.sidebar.selectbox("Select Station", stations)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", 
                pd.to_datetime("2021-01-01")
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                pd.to_datetime("2021-12-31")
            )
        
        return station, start_date, end_date
    
    @staticmethod
    def render_download_section(df: pd.DataFrame, station: str, 
                                start_date: date, end_date: date):
        """
        Render download section
        
        Args:
            df: DataFrame to download
            station: Station name
            start_date: Filter start date
            end_date: Filter end date
        """
        st.sidebar.header("💾 Download")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name=f"{station}_filtered_data_{start_date}_{end_date}.csv",
            mime="text/csv",
            key="download_button"
        )


class Metrics:
    """Class to display metrics"""
    
    @staticmethod
    def render_summary(df: pd.DataFrame):
        """
        Render summary metrics
        
        Args:
            df: DataFrame with data
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df))
        
        with col2:
            if 'Dates' in df.columns:
                date_min = df['Dates'].min()
                date_max = df['Dates'].max()
                st.metric("Date Range", f"{date_min.date()} to {date_max.date()}")
            else:
                st.metric("Date Range", "N/A")
        
        with col3:
            st.metric("Parameters", len(df.columns) - 1)


class Filters:
    """Class to handle visualization filters"""
    
    @staticmethod
    def render_chart_selection(chart_types: List[str]) -> str:
        """
        Render chart type selection
        
        Args:
            chart_types: Available chart types
        
        Returns:
            str: Selected chart type
        """
        return st.selectbox("Select Graph Type", chart_types)
    
    @staticmethod
    def render_column_selection(columns: List[str], chart_type: str) -> List[str]:
        """
        Render column selection based on chart type
        
        Args:
            columns: Available columns
            chart_type: Selected chart type
        
        Returns:
            List[str]: Selected columns
        """
        if chart_type in ["Line Chart", "Area Chart"]:
            selected = st.multiselect(
                "Select Parameters to Plot",
                columns,
                default=[columns[0]] if columns else []
            )
            return selected if selected else []
        else:
            selected = st.selectbox("Select Parameter to Plot", columns)
            return [selected] if selected else []


class DataDisplay:
    """Class to display data"""
    
    @staticmethod
    def render_dataframe(df: pd.DataFrame, expanded: bool = False):
        """
        Render dataframe in expandable section
        
        Args:
            df: DataFrame to display
            expanded: Whether to expand by default
        """
        with st.expander("📋 View Raw Data", expanded=expanded):
            st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def render_statistics(df: pd.DataFrame, columns: List[str]):
        """
        Render statistical summary
        
        Args:
            df: DataFrame
            columns: Columns to summarize
        """
        with st.expander("📊 Statistical Summary"):
            st.dataframe(df[columns].describe(), use_container_width=True)
import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from config.settings import settings
from database.bigquery_client import BigQueryClient
from database.queries import QueryBuilder
from analysis.ct_analysis import CTAnalysis
from analysis.tus_analysis import TUSAnalysis
from utils.data_processor import DataProcessor
from ui.components import Sidebar, Metrics, Filters, DataDisplay
from visualization.chart_implementations import ChartFactory

# Page configuration
st.set_page_config(
    page_title=settings.app.page_title,
    layout=settings.app.layout,
    initial_sidebar_state=settings.app.initial_sidebar_state
)

# Initialize session state
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False
if 'current_station' not in st.session_state:
    st.session_state.current_station = None

def init_clients():
    """Initialize BigQuery client"""
    return BigQueryClient()

def process_and_upload_data(uploaded_file, bq_client):
    """Process uploaded file and upload to BigQuery"""
    with st.spinner("Processing file..."):
        # Read file
        df = DataProcessor.read_file(uploaded_file)
        
        if df is None:
            return False
        
        # Check which stations are present
        if 'Station_ID' not in df.columns:
            st.error("File must contain 'Station_ID' column")
            return False
        
        stations = df['Station_ID'].unique()
        
        # Process each station
        for station in stations:
            if station == 'CT':
                analyzer = CTAnalysis()
                table_id = settings.bigquery.ct_table
            elif station == 'TUS':
                analyzer = TUSAnalysis()
                table_id = settings.bigquery.tus_table
            else:
                st.warning(f"Unknown station: {station}. Skipping...")
                continue
            
            try:
                # Process station data
                processed_df = analyzer.process(df)
                
                # Upload to BigQuery
                success = bq_client.upload_dataframe(processed_df, table_id)
                
                if success:
                    st.success(f"✅ {station} data processed and uploaded successfully!")
                else:
                    st.error(f"❌ Failed to upload {station} data")
                    return False
                    
            except Exception as e:
                st.error(f"Error processing {station} data: {str(e)}")
                return False
        
        return True

def load_station_data(bq_client, station, start_date, end_date):
    """Load data for selected station and date range"""
    table_id = settings.station_tables[station]
    
    # Check if table exists
    if not bq_client.table_exists(table_id):
        st.warning(f"No data available for {station} station. Please upload data first.")
        return None
    
    # Build and execute query
    query = QueryBuilder.get_filtered_data(table_id, start_date, end_date)
    df = bq_client.query(query)
    
    return df

def render_visualizations(df, station):
    """Render visualizations section"""
    st.header("📊 Data Visualization")
    
    # Get numeric columns for plotting
    numeric_cols = DataProcessor.get_numeric_columns(df)
    
    if not numeric_cols:
        st.warning("No numeric columns available for visualization")
        return
    
    # Chart selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        chart_types = ChartFactory.get_available_charts()
        chart_type = Filters.render_chart_selection(chart_types)
    
    with col2:
        selected_cols = Filters.render_column_selection(numeric_cols, chart_type)
    
    if selected_cols:
        try:
            # Create chart
            chart = ChartFactory.create_chart(
                chart_type,
                title=f"{station} Station - {chart_type}",
                xaxis_title="Date",
                yaxis_title="Value"
            )
            
            fig = chart.create(df, selected_cols)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    else:
        st.info("Please select parameters to plot")

def render_data_analysis(df):
    """Render data analysis section"""
    st.header("📈 Data Analysis")
    
    # Display metrics
    Metrics.render_summary(df)
    
    # Get numeric columns
    numeric_cols = DataProcessor.get_numeric_columns(df)
    
    if numeric_cols:
        # Statistical summary
        DataDisplay.render_statistics(df, numeric_cols)
    
    # Raw data view
    DataDisplay.render_dataframe(df, expanded=False)

def main():
    """Main application"""
    
    # Initialize
    bq_client = init_clients()
    
    # Title
    st.title("🌊 Water Quality Analysis Dashboard")
    st.markdown("---")
    
    # Sidebar - Upload Section
    uploaded_file = Sidebar.render_upload_section(st.session_state.uploaded)
    
    if uploaded_file == "RESET":
        st.session_state.uploaded = False
        st.rerun()
    
    if uploaded_file and not st.session_state.uploaded:
        if process_and_upload_data(uploaded_file, bq_client):
            st.session_state.uploaded = True
            st.rerun()
    
    # Sidebar - Filters
    if st.session_state.uploaded:
        stations = list(settings.station_tables.keys())
        station, start_date, end_date = Sidebar.render_filters(stations)
        
        # Load data
        with st.spinner(f"Loading {station} data..."):
            df = load_station_data(bq_client, station, start_date, end_date)
        
        if df is not None and not df.empty:
            # Store current station
            st.session_state.current_station = station
            
            # Display info
            st.success(f"📍 Showing data for **{station}** station from **{start_date}** to **{end_date}**")
            
            # Render visualizations
            render_visualizations(df, station)
            
            st.markdown("---")
            
            # Render analysis
            render_data_analysis(df)
            
            # Download section
            Sidebar.render_download_section(df, station, start_date, end_date)
            
        elif df is not None and df.empty:
            st.info(f"No data found for {station} station in the selected date range.")
        
    else:
        # Welcome message
        st.info("👆 Please upload water quality data to begin analysis")
        
        st.markdown("""
        ### 📋 Instructions
        
        1. **Upload Data**: Click on the file uploader in the sidebar and select your Excel or CSV file
        2. **Select Station**: Choose between CT or TUS station
        3. **Filter by Date**: Set your desired date range
        4. **Visualize**: Select chart type and parameters to visualize
        5. **Download**: Export filtered data as CSV
        
        ### 📊 Features
        
        - ✅ Automated data processing for CT and TUS stations
        - ✅ Interactive visualizations (Line, Scatter, Bar, Area charts)
        - ✅ Statistical analysis and summaries
        - ✅ Date range filtering
        - ✅ Data export functionality
        - ✅ Cloud storage with BigQuery
        """)

if __name__ == "__main__":
    main()
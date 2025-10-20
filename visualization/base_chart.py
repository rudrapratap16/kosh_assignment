import pandas as pd
import plotly.graph_objects as go
from abc import ABC, abstractmethod
from typing import List, Optional

class BaseChart(ABC):
    """Abstract base class for all chart types"""
    
    def __init__(self, title: str = "", xaxis_title: str = "Date", yaxis_title: str = "Value"):
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.fig = go.Figure()
    
    @abstractmethod
    def create(self, df: pd.DataFrame, columns: List[str], **kwargs) -> go.Figure:
        """
        Create the chart
        
        Args:
            df: DataFrame containing the data
            columns: List of column names to plot
            **kwargs: Additional parameters
        
        Returns:
            go.Figure: Plotly figure object
        """
        pass
    
    def update_layout(self, **kwargs):
        """Update the figure layout with common settings"""
        layout_config = {
            'title': self.title,
            'xaxis_title': self.xaxis_title,
            'yaxis_title': self.yaxis_title,
            'hovermode': 'x unified',
            'template': 'plotly_white',
            'showlegend': True
        }
        layout_config.update(kwargs)
        self.fig.update_layout(**layout_config)
    
    def validate_data(self, df: pd.DataFrame, columns: List[str]):
        """
        Validate that DataFrame has required columns and data
        
        Args:
            df: DataFrame to validate
            columns: Required columns
        
        Raises:
            ValueError: If validation fails
        """
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        if 'Dates' not in df.columns:
            raise ValueError("DataFrame must have 'Dates' column")
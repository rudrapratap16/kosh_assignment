import pandas as pd
import plotly.graph_objects as go
from typing import List
from visualization.base_chart import BaseChart

class LineChart(BaseChart):
    """Line chart implementation"""
    
    def create(self, df: pd.DataFrame, columns: List[str], **kwargs) -> go.Figure:
        """Create a line chart"""
        self.validate_data(df, columns)
        
        for col in columns:
            self.fig.add_trace(go.Scatter(
                x=df['Dates'],
                y=df[col],
                mode='lines+markers',
                name=col,
                line=dict(width=2),
                marker=dict(size=6)
            ))
        
        self.update_layout()
        return self.fig


class ScatterChart(BaseChart):
    """Scatter chart implementation"""
    
    def create(self, df: pd.DataFrame, columns: List[str], **kwargs) -> go.Figure:
        """Create a scatter chart"""
        self.validate_data(df, columns)
        
        col = columns[0]  # Scatter plot uses single column
        self.fig.add_trace(go.Scatter(
            x=df['Dates'],
            y=df[col],
            mode='markers',
            name=col,
            marker=dict(
                size=8,
                opacity=0.7,
                color=df[col],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=col)
            )
        ))
        
        self.update_layout()
        return self.fig


class BarChart(BaseChart):
    """Bar chart implementation"""
    
    def create(self, df: pd.DataFrame, columns: List[str], **kwargs) -> go.Figure:
        """Create a bar chart"""
        self.validate_data(df, columns)
        
        col = columns[0]  # Bar chart uses single column
        self.fig.add_trace(go.Bar(
            x=df['Dates'],
            y=df[col],
            name=col,
            marker=dict(
                color=df[col],
                colorscale='Blues'
            )
        ))
        
        self.update_layout()
        return self.fig


class AreaChart(BaseChart):
    """Area chart implementation"""
    
    def create(self, df: pd.DataFrame, columns: List[str], **kwargs) -> go.Figure:
        """Create an area chart"""
        self.validate_data(df, columns)
        
        for idx, col in enumerate(columns):
            self.fig.add_trace(go.Scatter(
                x=df['Dates'],
                y=df[col],
                mode='lines',
                name=col,
                fill='tonexty' if idx > 0 else 'tozeroy',
                line=dict(width=2)
            ))
        
        self.update_layout()
        return self.fig


class ChartFactory:
    """Factory class to create charts"""
    
    CHART_TYPES = {
        "Line Chart": LineChart,
        "Scatter Plot": ScatterChart,
        "Bar Chart": BarChart,
        "Area Chart": AreaChart
    }
    
    @staticmethod
    def create_chart(chart_type: str, title: str = "", xaxis_title: str = "Date", 
                     yaxis_title: str = "Value") -> BaseChart:
        """
        Create a chart instance based on type
        
        Args:
            chart_type: Type of chart to create
            title: Chart title
            xaxis_title: X-axis label
            yaxis_title: Y-axis label
        
        Returns:
            BaseChart: Chart instance
        
        Raises:
            ValueError: If chart type is not supported
        """
        if chart_type not in ChartFactory.CHART_TYPES:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        chart_class = ChartFactory.CHART_TYPES[chart_type]
        return chart_class(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    
    @staticmethod
    def get_available_charts() -> List[str]:
        """Get list of available chart types"""
        return list(ChartFactory.CHART_TYPES.keys())
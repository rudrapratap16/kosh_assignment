import os
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass
class BigQueryConfig:
    """BigQuery configuration settings"""
    project_id: str
    dataset_id: str
    ct_table: str
    tus_table: str
    credentials_path: str

@dataclass
class AppConfig:
    """Application configuration settings"""
    page_title: str = "Water Quality Dashboard"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    cache_ttl: int = 600  # 10 minutes

class Settings:
    """Main settings class to manage all configurations"""
    
    def __init__(self):
        load_dotenv()
        self._load_bigquery_config()
        self.app = AppConfig()
    
    def _load_bigquery_config(self):
        """Load BigQuery configuration from environment variables"""
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        project_id = "koshai-475618"
        dataset_id = f"{project_id}.water_analysis"
        
        self.bigquery = BigQueryConfig(
            project_id=project_id,
            dataset_id=dataset_id,
            ct_table=f"{dataset_id}.ct_analysis",
            tus_table=f"{dataset_id}.tus_analysis",
            credentials_path=credentials_path
        )
    
    @property
    def station_tables(self):
        """Return dictionary of station names to table IDs"""
        return {
            "CT": self.bigquery.ct_table,
            "TUS": self.bigquery.tus_table
        }

# Global settings instance
settings = Settings()
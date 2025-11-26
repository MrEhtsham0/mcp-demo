from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import SecretStr
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Expense Tracker AI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "Expense Tracker"
    
    mysql_host: str = "expensetracker.cvk260qia0fj.eu-north-1.rds.amazonaws.com"
    mysql_port: int = 3306
    mysql_user: str = "admin"
    mysql_password: str = "expensetracker"
    mysql_database: str = "UserDB"
    
    # Database Pool Settings
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_max_connections: int = 10
    
    # Cache Settings
    cache_default_ttl: int = 300  # 5 minutes
    cache_expense_ttl: int = 600  # 10 minutes
    cache_summary_ttl: int = 1800  # 30 minutes
    
    # Password Configuration
    password_min_length: int = 8
    password_require_special_chars: bool = True
    
    # External Services
    openai_api_key: SecretStr = SecretStr("")
    tavily_api_key: SecretStr = SecretStr("")
    backend_cors_origins: List[str] = ["*"]
    
    aws_access_key_id: SecretStr
    aws_secret_access_key: SecretStr
    aws_region:str
    aws_s3_bucket_name: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False
        
    )
    
    @property
    def async_database_url(self) -> str:
        """Get async MySQL database URL"""
        return f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

# Global settings instance
settings = Settings()
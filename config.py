from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # MySQL Database Configuration (Docker)
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "expense_user"
    mysql_password: str = "expense_password"
    mysql_database: str = "expense_tracker"
    categories_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "categories.json")

    
    # Application Settings
    app_name: str = "Expense Tracker MCP Server"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Get MySQL database URL"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    @property
    def async_database_url(self) -> str:
        """Get async MySQL database URL"""
        return f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

settings = Settings()
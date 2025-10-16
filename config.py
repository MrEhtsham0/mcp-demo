from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # AWS RDS MySQL Configuration
    mysql_host: str = "expense-tracker-db.cx0aeuk0edcm.eu-north-1.rds.amazonaws.com"
    mysql_port: int = 3306
    mysql_user: str = "expense_tracker"
    mysql_password: str = "expense-tracker-db"
    mysql_database: str = "expense_tracker"
    categories_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "categories.json")
    
    # Previous Docker MySQL Configuration (commented out)
    # mysql_host: str = "localhost"
    # mysql_port: int = 3306
    # mysql_user: str = "expense_user"
    # mysql_password: str = "expense_password"
    # mysql_database: str = "expense_tracker"

    
    # Application Settings
    app_name: str = "Expense Tracker MCP Server"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Get MySQL database URL for AWS RDS"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    @property
    def async_database_url(self) -> str:
        """Get async MySQL database URL for AWS RDS"""
        return f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

settings = Settings()
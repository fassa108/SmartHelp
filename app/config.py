from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Support Ticket Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
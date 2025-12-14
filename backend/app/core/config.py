from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "B2B RFP Agent"
    API_V1_STR: str = "/api/v1"
    
    # CORS - Allow all for MVP
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    # SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"
    
    # LLM Keys
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

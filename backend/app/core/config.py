"""
Core configuration settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    # 项目信息
    PROJECT_NAME: str = "NEMO FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # MySQL 数据库配置
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "12345678"
    MYSQL_DB: str = "szlab_appoint"
    MYSQL_PORT: int = 3306
    
    DATABASE_URL: str = "mysql+aiomysql://root:12345678@localhost:3306/szlab_appoint"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 超级管理员
    FIRST_SUPERUSER: str = "admin@nemo.local"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

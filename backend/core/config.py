from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "VulnScanner"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "sanchit-vulnscanner-secret-key-2026"

    # Database - MySQL
    DATABASE_URL: str = "mysql+pymysql://root:Sanchit%408984@localhost:3306/vulnscanner_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CELERY_BROKER_URL: str = "redis://:redis_password@localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://:redis_password@localhost:6379/1"

    # OWASP ZAP
    ZAP_PROXY_HOST: str = "localhost"
    ZAP_PROXY_PORT: int = 8090
    ZAP_API_KEY: str = "change-this-key"
    ZAP_ENABLED: bool = True

    # Scan Configuration
    MAX_CONCURRENT_SCANS: int = 5
    SCAN_TIMEOUT: int = 3600
    MAX_SCAN_DEPTH: int = 5
    REQUEST_TIMEOUT: int = 30
    ENABLE_ADVANCED_SCANS: bool = True

    # Security & Authentication
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    CORS_ENABLED: bool = True
    JWT_SECRET_KEY: str = "sanchit-jwt-secret-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Reports
    REPORT_STORAGE_PATH: str = "./reports"
    MAX_REPORT_AGE_DAYS: int = 30

    # Email Notifications
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ENABLE_EMAIL_NOTIFICATIONS: bool = False

    # Scheduled Scans
    ENABLE_SCHEDULED_SCANS: bool = True
    SCHEDULER_TIMEZONE: str = "Asia/Kolkata"

    class Config:
        env_file = ("../.env", ".env")
        case_sensitive = True
        extra = "ignore"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()

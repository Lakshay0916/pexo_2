from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Pexo - Payroll Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/Pexo"
    DB_SCHEMA: str = "public"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "supersecretjwtkey_change_in_production_Pexo"
    ALGORITHM: str = "HS256"

    HR_SERVICE_URL: str = "http://localhost:8001"
    ATTENDANCE_SERVICE_URL: str = "http://localhost:8002"
    AZURE_STORAGE_CONNECTION_STRING: str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;"
    AZURE_CONTAINER_NAME: str = "payslips"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

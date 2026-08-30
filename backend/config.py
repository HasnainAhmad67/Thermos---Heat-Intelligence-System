from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    fortyguard_api_key: str = ""
    fortyguard_base_url: str = "https://api.fortyguard.com"
    gemini_api_key: str = ""
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
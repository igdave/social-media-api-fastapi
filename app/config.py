import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically find the absolute path to your project root directory
current_dir = os.path.dirname(os.path.abspath(__file__)) # inside 'app' folder
project_root = os.path.dirname(current_dir)             # moves up to project root
env_file_path = os.path.join(project_root, ".env")

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Pass the calculated absolute string path here
    model_config = SettingsConfigDict(env_file=env_file_path)

settings = Settings()

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Agile AI Vision Backend API"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str = "sqlite:///./data/database/metadata.db" # Default path, can be overridden by env var

    # File storage settings
    IMAGE_STORAGE_BASE_PATH: str = "./data/images" # Default path

    # Model Server URLs (examples, actual URLs will depend on deployment)
    YOLO_UNIOW_SERVER_URL: str = "http://yolo_uniow_model_server:8001/infer" # Assuming port 8001 for yolo server
    GROUNDING_DINO_SERVER_URL: str = "http://grounding_dino_model_server:8002/infer"
    GLIGEN_SERVER_URL: str = "http://gligen_model_server:8003/generate"
    CONTROLNET_SERVER_URL: str = "http://controlnet_model_server:8004/edit"
    INTERNVL2_SERVER_URL: str = "http://internvl2_model_server:8005/suggest"

    class Config:
        env_file = ".env" # Load environment variables from .env file if it exists
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

if __name__ == "__main__":
    # Print settings to verify
    print("Current Settings:")
    for key, value in settings.dict().items():
        print(f"{key}: {value}")
```

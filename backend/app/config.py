from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Get the directory of this config file
config_dir = Path(__file__).parent.parent
env_file_path = config_dir / ".env"

class Settings(BaseSettings):
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    OPENROUTER_API_KEY: str

    class Config:
        env_file = str(env_file_path)
        case_sensitive = False

# Load settings, handling missing .env gracefully
try:
    settings = Settings()
except Exception as e:
    # Try loading from environment variables directly
    settings = Settings(
        NEO4J_URI=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        NEO4J_USER=os.getenv("NEO4J_USER", "neo4j"),
        NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD", ""),
        OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", "")
    )

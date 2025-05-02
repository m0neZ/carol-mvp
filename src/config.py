import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Example environment variables (add more as needed)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN") # For webhook verification
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "secret")

# You can add more configuration settings here
class Settings:
    PROJECT_NAME: str = "ShopperGPT"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = DATABASE_URL
    OPENAI_API_KEY: str = OPENAI_API_KEY
    WHATSAPP_API_TOKEN: str = WHATSAPP_API_TOKEN
    WHATSAPP_VERIFY_TOKEN: str = WHATSAPP_VERIFY_TOKEN
    ADMIN_USERNAME: str = ADMIN_USERNAME
    ADMIN_PASSWORD: str = ADMIN_PASSWORD

settings = Settings()


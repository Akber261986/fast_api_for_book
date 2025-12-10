import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variables:")
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"QDRANT_API_KEY: {os.getenv('QDRANT_API_KEY')}")
print(f"QDRANT_HOST: {os.getenv('QDRANT_HOST')}")

# Now test the settings
from app.config.settings import settings
print("\nSettings from pydantic:")
print(f"settings.gemini_api_key: {settings.gemini_api_key}")
print(f"settings.openai_api_key: {settings.openai_api_key}")
print(f"settings.qdrant_api_key: {settings.qdrant_api_key}")
print(f"settings.qdrant_host: {settings.qdrant_host}")
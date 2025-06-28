import os
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.getenv("JWT_KEY", "your_super_secret_key")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/appdata")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY","dummy_key_for_no_op")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "MISTRAL_KEY_HERE")
LLM_BACKEND = os.getenv("LLM_BACKEND", "gemini")
import os
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.getenv("JWT_KEY", "your_super_secret_key")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sqai_2_user:p86H82KAFjTqSTYkF3jPaKMCHGZ6YxZF@dpg-d1fr2qmmcj7s73c0cisg-a/sqai_2")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY","dummy_key_for_no_op")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "MISTRAL_KEY_HERE")
LLM_BACKEND = os.getenv("LLM_BACKEND", "gemini")

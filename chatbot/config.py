# chatbot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

if not TELEGRAM_TOKEN:
    raise ValueError("No se encontró TELEGRAM_TOKEN en las variables de entorno.")
if not API_BASE_URL:
    raise ValueError("No se encontró API_BASE_URL en las variables de entorno.")
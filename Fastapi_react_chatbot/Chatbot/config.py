# chatbot/config.py

import os
from dotenv import load_dotenv

# Carga variables de entorno desde un archivo .env en la raíz del proyecto del chatbot
load_dotenv()

# --- Configuración de Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Configuración de la API de Backend ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Configuración del LLM ---
# Reemplaza estas variables según el proveedor de LLM que uses (OpenAI, Google, DeepSeek, etc.)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "deepseek-chat") # O "deepseek-coder"


# --- Validar configuraciones necesarias ---
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno. "
                     "Crea un archivo .env con TELEGRAM_BOT_TOKEN=tu_token_aqui")

# Para este paso, el LLM es opcional, pero si LLM_API_KEY está configurado, también requerimos la URL
if LLM_API_KEY and not LLM_API_URL:
     raise ValueError("LLM_API_KEY está configurado, pero LLM_API_URL no. "
                      "Asegúrate de configurar ambas si quieres usar un LLM.")


# --- Otros configuraciones ---
# ...
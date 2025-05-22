# Archivo: chatbot/config.py
# Configuración para el chatbot, incluyendo tokens y URLs.

import os
from dotenv import load_dotenv

# Carga variables de entorno desde un archivo .env si lo estás utilizando.
# Crea un archivo .env en la raíz de tu proyecto chatbot con el siguiente contenido:
# TELEGRAM_BOT_TOKEN="TU_TOKEN_DE_TELEGRAM"
# GEMINI_API_KEY="TU_GEMINI_API_KEY"
# API_BASE_URL="http://localhost:8000/api/v1" (o la URL de tu backend desplegado)
# LOG_LEVEL="INFO"
load_dotenv()

# --- Tokens y Claves API ---
# Token de tu bot de Telegram. Obtenlo de BotFather.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Tu API Key para el servicio de Gemini (Google AI Studio).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# --- URLs de Servicios ---
# URL base de tu API backend (FastAPI).
# Asegúrate que esta URL sea accesible desde donde corre tu bot.
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


# --- Configuraciones de Logging ---
# Nivel de logging para la aplicación. Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# --- Validaciones de Configuración Esencial ---
# Es crucial que las configuraciones críticas estén presentes al iniciar.
if not TELEGRAM_BOT_TOKEN:
    # Usamos print aquí porque el logger podría no estar configurado aún.
    print("ERROR CRÍTICO: TELEGRAM_BOT_TOKEN no está configurado. El bot no puede iniciar.")
    print("Por favor, define TELEGRAM_BOT_TOKEN en tus variables de entorno o en un archivo .env.")
    exit(1) # Detiene la ejecución si falta el token del bot.

if not GEMINI_API_KEY:
    print("ERROR CRÍTICO: GEMINI_API_KEY no está configurado. El bot no puede iniciar.")
    print("Por favor, define GEMINI_API_KEY en tus variables de entorno o en un archivo .env.")
    exit(1) # Detiene la ejecución si falta la clave de Gemini.

if not API_BASE_URL:
    print("ADVERTENCIA: API_BASE_URL no está configurada. Usando valor por defecto 'http://localhost:8000/api/v1'.")
    # No salimos, pero es una advertencia importante.

# Puedes añadir otras configuraciones globales aquí, por ejemplo:
# ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") # Para enviar notificaciones de error, etc.


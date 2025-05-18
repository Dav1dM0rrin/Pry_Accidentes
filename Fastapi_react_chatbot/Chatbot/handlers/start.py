# chatbot/handlers/start.py

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje de bienvenida cuando se recibe el comando /start."""
    user = update.effective_user
    logger.info(f"Comando /start recibido de usuario {user.id} ({user.username or user.first_name})")
    await update.message.reply_html(
        f"¡Hola, {user.mention_html()}! Soy un bot sobre accidentes en Barranquilla. "
        "Puedes usar el comando /ultimos10 para ver los 10 accidentes más recientes."
        # Añade aquí otros comandos a medida que los implementes
    )
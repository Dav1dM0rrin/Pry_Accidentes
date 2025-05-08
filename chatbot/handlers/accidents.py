# chatbot/handlers/accidents.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

# Importa la función refactorizada del api_client
from ..api_client import get_and_format_last_n_accidentes

logger = logging.getLogger(__name__)

async def ultimos_10_accidentes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /ultimos10 usando la función refactorizada del api_client."""
    logger.info(f"Comando /ultimos10 recibido de usuario {update.effective_user.id}")

    # Llama a la función refactorizada del api_client para obtener el mensaje formateado
    reply_text = get_and_format_last_n_accidentes(10)

    # Envía el mensaje
    await update.message.reply_text(reply_text)
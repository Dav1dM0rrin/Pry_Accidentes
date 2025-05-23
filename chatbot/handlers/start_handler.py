# chatbot/handlers/start_handler.py
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler # CallbackContext es importado pero no usado directamente en esta versión de PTB para type hints de context
from telegram.constants import ParseMode
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) inició el bot con /start.")
    welcome_message = (
        f"¡Hola, {user.first_name}!\n\n"
        "Soy tu asistente para el reporte y consulta de accidentes en Barranquilla.\n\n"
        "Puedes usar los siguientes comandos:\n"
        "📍 /reportar - Para reportar un nuevo accidente.\n"
        "📄 /detalle_accidente (ID) - Para ver los últimos N accidentes (ej: /ver_accidentes <code>5</code>).\n" # CAMBIO
        "ℹ️ /help - Para mostrar este mensaje de ayuda nuevamente.\n\n"
        "Escribe el comando que necesites. ¡Estoy aquí para ayudarte!"
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)

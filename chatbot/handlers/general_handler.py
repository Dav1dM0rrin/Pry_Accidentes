# chatbot/handlers/general_handler.py
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
import logging
from ..llm_service import LLMService

logger = logging.getLogger(__name__)
llm_service = LLMService()

async def help_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) solicitó ayuda con /help.")
    help_text = (
        "¡Claro! Aquí tienes los comandos disponibles:\n\n"
        "📍 /reportar_accidente - Inicia el proceso para reportar un nuevo accidente.\n"
        "📄 /ver_accidentes <code>N</code> - Muestra los últimos N accidentes reportados. Si no especificas N, se mostrarán 3 por defecto. Ejemplo: /ver_accidentes <code>5</code>\n" # CAMBIO
        "🔍 /detalle_accidente <code>ID</code> - Muestra los detalles de un accidente por su ID. Ejemplo: /detalle_accidente <code>123</code>\n" # CAMBIO
        "🤖 /chat_ia <code>tu pregunta</code> - Interactúa con una IA para consultas generales. Ejemplo: /chat_ia <code>¿Qué es un accidente?</code>\n" # CAMBIO
        "👋 /start - Muestra el mensaje de bienvenida.\n"
        "ℹ️ /help - Muestra este mensaje de ayuda.\n\n"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

async def chat_ia_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    prompt_parts = context.args
    
    if not llm_service.model:
        await update.message.reply_text("Lo siento, el servicio de IA no está disponible en este momento.")
        return

    if not prompt_parts:
        await update.message.reply_text("Por favor, escribe tu pregunta después del comando /chat_ia.\nEjemplo: /chat_ia <code>¿Qué es un accidente?</code>", parse_mode=ParseMode.HTML) # CAMBIO
        return

    prompt = " ".join(prompt_parts)
    logger.info(f"Usuario {user.id} ({user.username}) envió prompt a IA: '{prompt}'")
    
    await update.message.reply_chat_action('typing')
    response_text = await llm_service.get_llm_response(prompt)
    
    if response_text:
        await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("No pude obtener una respuesta del servicio de IA en este momento.")

async def unknown_command(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Usuario {update.effective_user.id} envió un comando desconocido: {update.message.text}")
    await update.message.reply_text("Lo siento, no entendí ese comando. Prueba con /help.")

# Archivo: chatbot/main_bot.py
# Punto de entrada principal para configurar e iniciar el bot de Telegram.

import asyncio 
from telegram import Update 
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters, 
)

# --- Importaciones de Módulos del Proyecto ---
from chatbot.config import TELEGRAM_BOT_TOKEN, LOG_LEVEL 
from chatbot.bot_logging import logger, setup_logging 

from chatbot.handlers import start_handler 
from chatbot.handlers.general_handler import general_message_handler, reset_chat_command 

from chatbot.handlers.accident_handler import (
    report_accident_conversation_handler, 
    detalle_accidente_command,            
    handle_natural_language_accident_query 
)

def main() -> None:
    setup_logging(level_name=LOG_LEVEL) 
    logger.info("============================================================")
    logger.info("🚀 INICIANDO BOT ASISTENTE VIAL BARRANQUILLA 🚀")
    logger.info("============================================================")

    if not TELEGRAM_BOT_TOKEN: 
        logger.critical("CRÍTICO: TELEGRAM_BOT_TOKEN no encontrado.")
        return 

    application_builder = Application.builder().token(TELEGRAM_BOT_TOKEN)
    application_builder.read_timeout(30)  
    application_builder.write_timeout(30) 
    application_builder.connect_timeout(30)
    application = application_builder.build()
    
    async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(msg="EXCEPCIÓN NO MANEJADA AL PROCESAR UN UPDATE:", exc_info=context.error)
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🚧 ¡Ups! Parece que encontré un bache en el camino (un error inesperado) al procesar tu solicitud. 🚧\n"
                         "El equipo técnico ya ha sido notificado. Por favor, intenta de nuevo en unos momentos."
                )
            except Exception as e_notify:
                logger.error(f"Error al intentar enviar mensaje de error al usuario {update.effective_chat.id}: {e_notify}")
    application.add_error_handler(global_error_handler)

    logger.info("Registrando handlers...")

    # Grupo 0 (por defecto) para handlers más específicos o que deben evaluarse primero.
    application.add_handler(CommandHandler(["start", "ayuda", "help"], start_handler.start), group=0)
    logger.debug("Handler para /start, /ayuda, /help registrado en grupo 0.")

    application.add_handler(CommandHandler("reset_chat", reset_chat_command), group=0)
    logger.debug("Handler para /reset_chat registrado en grupo 0.")

    application.add_handler(report_accident_conversation_handler, group=0) # ConversationHandlers también pueden tener grupo.
    logger.debug("ConversationHandler para reporte de accidentes registrado en grupo 0.")

    application.add_handler(CommandHandler("detalle_accidente", detalle_accidente_command), group=0)
    logger.debug("CommandHandler para /detalle_accidente registrado en grupo 0.")

    # MessageHandler para buscar IDs en lenguaje natural, también en grupo 0.
    # Se ejecutará después de los CommandHandlers dentro del mismo grupo si los filtros coinciden.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_accident_query), group=0)
    logger.debug("MessageHandler para consultas de accidentes en lenguaje natural (busca IDs) registrado en grupo 0.")
    
    # MessageHandler general (LLM) en un grupo posterior (grupo 1).
    # Se ejecutará si ningún handler en el grupo 0 manejó completamente el update.
    application.add_handler(general_message_handler, group=1) 
    logger.debug("MessageHandler general para texto (LLM) registrado en grupo 1.")
    
    # Fallback para comandos desconocidos (opcional, en un grupo aún posterior o el mismo que el LLM general).
    async def unknown_command_or_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message and update.message.text: 
            if update.message.text.startswith('/'):
                logger.warning(f"Comando desconocido recibido: {update.message.text} de user_id {update.effective_user.id if update.effective_user else 'N/A'}")
                await update.message.reply_text(
                    "🤔 Lo siento, no reconozco ese comando.\n"
                    "Puedes intentar con /start o /ayuda para ver las opciones disponibles."
                )
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command_or_message_handler), group=2) # Ejemplo en grupo 2
    logger.debug("MessageHandler para comandos desconocidos registrado en grupo 2.")
    
    logger.info("🤖 Bot configurado y listo. Iniciando polling...")
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES, 
            drop_pending_updates=True, 
        )
    except KeyboardInterrupt:
        logger.info("Polling detenido manualmente (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"El bot se detuvo debido a un error crítico no manejado durante el polling: {e}", exc_info=True)
    finally:
        logger.info("============================================================")
        logger.info("🛑 BOT DETENIDO 🛑")
        logger.info("============================================================")

if __name__ == "__main__":
    main()

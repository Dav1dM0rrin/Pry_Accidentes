# chatbot/bot.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Importa la configuración
from .config import TELEGRAM_BOT_TOKEN, LLM_API_KEY # Importa también LLM_API_KEY

# Importa los manejadores
from .handlers.start import start
from .handlers.accidents import ultimos_10_accidentes_handler
from .handlers.general import handle_text_message # Importa el nuevo manejador general

# Configura el logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main() -> None:
    """Inicia el bot de Telegram."""
    
    # Verifica que el token de Telegram esté cargado
    if not TELEGRAM_BOT_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN no está configurado. Asegúrate de tener un archivo .env válido.")
        return

    # Crea la aplicación del bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra los handlers de comandos (tienen prioridad sobre MessageHandler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ultimos10", ultimos_10_accidentes_handler))

    # Registra el manejador general de mensajes de texto
    # Usa filters.TEXT para mensajes de texto y ~filters.COMMAND para excluir comandos
    # Solo registramos este manejador si la clave del LLM está configurada
    if LLM_API_KEY:
        logging.info("LLM_API_KEY configurada. Registrando manejador general de texto.")
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    else:
        logging.warning("LLM_API_KEY no configurada. El bot solo responderá a comandos.")


    # Inicia el bot
    logging.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
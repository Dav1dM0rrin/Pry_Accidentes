# chatbot/main_bot.py
import logging
import asyncio # Importante para v21

# Importar configuración y logger primero
from .config import TELEGRAM_TOKEN
from .bot_logging import setup_logging

# Configurar logging ANTES de importar otros módulos que puedan usarlo
logger = setup_logging()

# Importar ApplicationBuilder y los handlers
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters

# Importar nuestros módulos de handlers
from .handlers.start_handler import start # Importar la función directamente
from .handlers.general_handler import help_command, chat_ia_command, unknown_command # Funciones directas
from .handlers.accident_handler import (
    report_accident_start, # Punto de entrada de la conversación
    get_description, get_latitude, get_longitude, get_gravity, confirm_report, # Estados
    cancel_report, # Fallback
    view_accidents, # Comandos individuales
    accident_detail
)
from .handlers.conversation_states import DESCRIPTION, LATITUDE, LONGITUDE, GRAVITY, CONFIRMATION # Estados

async def main() -> None: # La función main ahora es async
    """Inicia el bot de Telegram usando ApplicationBuilder (PTB v20+)."""
    logger.info("Iniciando el bot con PTB v21.x...")

    if not TELEGRAM_TOKEN:
        logger.critical("TELEGRAM_TOKEN no está configurado. El bot no puede iniciar.")
        return

    # Crear la Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # --- Configuración del ConversationHandler para /reportar_accidente ---
    report_accident_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("reportar_accidente", report_accident_start)],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            LATITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_latitude)],
            LONGITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_longitude)],
            GRAVITY: [MessageHandler(filters.Regex('^(Leve|Moderado|Grave)$') & ~filters.COMMAND, get_gravity)],
            CONFIRMATION: [MessageHandler(filters.Regex('^(Sí|Si|No|sí|si|no)$') & ~filters.COMMAND, confirm_report)],
        },
        fallbacks=[CommandHandler("cancelar", cancel_report)],
        # Opcional: persistencia de conversación (ej. en memoria o archivos)
        # name="report_accident_conversation", # Nombre para la persistencia
        # persistent=True, # Requiere configurar un persister
    )

    # Registrar handlers en la aplicación
    application.add_handler(report_accident_conv_handler) # ConversationHandler primero

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat_ia", chat_ia_command))
    application.add_handler(CommandHandler("ver_accidentes", view_accidents))
    application.add_handler(CommandHandler("detalle_accidente", accident_detail))
    
    # Registrar el MessageHandler para comandos desconocidos al final
    application.add_handler(MessageHandler(filters.COMMAND & (~filters.UpdateType.EDITED_MESSAGE), unknown_command))
    
    # Opcional: Manejador de errores global
    # async def error_handler(update, context):
    #    logger.error(f"Update {update} causó error {context.error}", exc_info=context.error)
    # application.add_error_handler(error_handler)

    # Iniciar el Bot
    try:
        logger.info("Bot iniciando polling...")
        await application.initialize() # Inicializar la aplicación
        await application.start()      # Iniciar el bot (no bloqueante)
        await application.updater.start_polling() # Iniciar el polling (no bloqueante)
        logger.info("Bot iniciado y escuchando actualizaciones...")
        
        # Mantener el script corriendo. En un entorno de producción, esto podría
        # ser manejado por un supervisor de procesos (systemd, Docker, etc.)
        # Para desarrollo, un bucle simple o simplemente dejar que asyncio maneje.
        while True:
            await asyncio.sleep(3600) # Dormir por un largo tiempo, o hasta que se interrumpa

    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot detenido por el usuario.")
    except Exception as e:
        logger.critical(f"Error crítico al ejecutar el bot: {e}", exc_info=True)
    finally:
        logger.info("Deteniendo el bot...")
        if application.updater and application.updater.running:
            await application.updater.stop()
        if application.running: # Comprobar si la aplicación está corriendo antes de apagar
            await application.stop()
        await application.shutdown() # Limpiar recursos
        logger.info("Bot detenido limpiamente.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Proceso principal interrumpido.")
    except Exception as e:
        logger.critical(f"Error al ejecutar asyncio.run(main()): {e}", exc_info=True)

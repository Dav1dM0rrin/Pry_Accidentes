# Archivo: chatbot/main_bot.py
# Punto de entrada principal para configurar e iniciar el bot de Telegram.

import asyncio # Aunque python-telegram-bot v20+ es async por defecto, puede ser útil para otras tareas.
from telegram import Update # Clase base para todos los tipos de updates.
from telegram.ext import (
    Application, # Clase principal para interactuar con la API de Telegram.
    CommandHandler, # Maneja comandos (ej. /start, /reportar).
    ContextTypes, # Usado para type hints del objeto `context`.
    MessageHandler, # Maneja mensajes regulares (texto, imágenes, etc.).
    filters, # Define filtros para los MessageHandlers (ej. texto, comando, etc.).
    # ConversationHandler ya está importado desde accident_handler.py.
)

# --- Importaciones de Módulos del Proyecto ---
from chatbot.config import TELEGRAM_BOT_TOKEN, LOG_LEVEL # Configuraciones esenciales.
from chatbot.bot_logging import logger, setup_logging # Utilidades de logging.

# Importar los manejadores (handlers) definidos en otros archivos.
from chatbot.handlers import start_handler # Para los comandos /start y /ayuda.
from chatbot.handlers.general_handler import general_message_handler, reset_chat_command # Para mensajes generales y /reset_chat.
from chatbot.handlers.accident_handler import report_accident_conversation_handler # El ConversationHandler para reportes.


def main() -> None:
    """
    Función principal que configura y ejecuta el bot de Telegram.
    """
    # --- 1. Configuración del Logging ---
    # Es importante configurar el logging al inicio para capturar todos los mensajes.
    # `setup_logging` debería tomar `LOG_LEVEL` de `config.py` para establecer el nivel.
    setup_logging(level_name=LOG_LEVEL) 
    logger.info("============================================================")
    logger.info("🚀 INICIANDO BOT ASISTENTE VIAL BARRANQUILLA 🚀")
    logger.info("============================================================")

    # --- 2. Validación del Token del Bot ---
    if not TELEGRAM_BOT_TOKEN: # Ya validado en config.py, pero doble chequeo no hace daño.
        logger.critical("CRÍTICO: TELEGRAM_BOT_TOKEN no encontrado. El bot no puede iniciar. Revisa tu configuración.")
        return # Salir si no hay token.

    # --- 3. Creación y Configuración de la Aplicación del Bot ---
    # `Application.builder()` es la forma moderna de crear la aplicación.
    application_builder = Application.builder().token(TELEGRAM_BOT_TOKEN)
    
    # Configuración de timeouts y pool size para `httpx` (usado internamente por PTB v20+).
    # Estos valores pueden necesitar ajuste según la carga y la red.
    application_builder.read_timeout(30)  # Segundos para esperar una respuesta de la API de Telegram.
    application_builder.write_timeout(30) # Segundos para esperar al enviar datos a la API de Telegram.
    application_builder.connect_timeout(30) # Segundos para establecer la conexión inicial.
    # application_builder.pool_timeout(20) # Timeout para obtener una conexión del pool HTTPX.
    # application_builder.connection_pool_size(10) # Tamaño del pool de conexiones HTTPX.
    # application_builder.concurrent_updates(True) # Para manejar múltiples updates concurrentemente. Ajustar según necesidad.

    application = application_builder.build()
    
    # --- 4. (Opcional pero Recomendado) Manejador de Errores Global ---
    # Este handler capturará excepciones no manejadas en otros handlers.
    async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Loguea los errores causados por Updates y notifica al usuario si es posible."""
        logger.error(msg="EXCEPCIÓN NO MANEJADA AL PROCESAR UN UPDATE:", exc_info=context.error)
        
        # Intentar notificar al usuario del error, si el `update` lo permite.
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🚧 ¡Ups! Parece que encontré un bache en el camino (un error inesperado) al procesar tu solicitud. 🚧\n"
                         "El equipo técnico ya ha sido notificado. Por favor, intenta de nuevo en unos momentos."
                )
            except Exception as e_notify:
                logger.error(f"Error al intentar enviar mensaje de error al usuario {update.effective_chat.id}: {e_notify}")
        # Aquí también podrías notificar a un chat de administrador si tienes `ADMIN_CHAT_ID` configurado.
        # if ADMIN_CHAT_ID:
        #     await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Error en bot: {context.error}")

    application.add_error_handler(global_error_handler)


    # --- 5. Registro de Handlers ---
    # El orden de registro de los handlers es importante.
    # Los más específicos (como CommandHandler o ConversationHandler) deben registrarse
    # ANTES que los más generales (como MessageHandler para texto genérico).

    # 5.1. Comandos básicos (/start, /ayuda)
    # Se asume que `start_handler.start` maneja ambos o tienes handlers separados.
    application.add_handler(CommandHandler(["start", "ayuda", "help"], start_handler.start))
    logger.debug("Handler para /start, /ayuda, /help registrado.")

    # 5.2. Comando para resetear el chat con el LLM (/reset_chat)
    application.add_handler(CommandHandler("reset_chat", reset_chat_command))
    logger.debug("Handler para /reset_chat registrado.")

    # 5.3. ConversationHandler para el reporte de accidentes (/reportar y sus pasos)
    # `report_accident_conversation_handler` está definido en `accident_handler.py`.
    application.add_handler(report_accident_conversation_handler)
    logger.debug("ConversationHandler para reporte de accidentes registrado.")

    # 5.4. MessageHandler para mensajes de texto generales (usa el LLM)
    # Este debe ir DESPUÉS de los CommandHandlers y ConversationHandlers para no interceptar
    # comandos o mensajes destinados a conversaciones activas.
    application.add_handler(general_message_handler)
    logger.debug("MessageHandler general para texto (LLM) registrado.")
    
    # 5.5. (Opcional) Handler para comandos desconocidos.
    # Debe ser uno de los últimos handlers de comandos/mensajes en registrarse.
    async def unknown_command_or_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Responde a comandos no reconocidos o mensajes que no encajan en otros handlers."""
        if update.message and update.message.text: # Asegurarse que es un mensaje de texto.
            # Si es un comando no reconocido.
            if update.message.text.startswith('/'):
                logger.warning(f"Comando desconocido recibido: {update.message.text} de user_id {update.effective_user.id if update.effective_user else 'N/A'}")
                await update.message.reply_text(
                    "🤔 Lo siento, no reconozco ese comando.\n"
                    "Puedes intentar con /start o /ayuda para ver las opciones disponibles y los comandos que entiendo."
                )
            # Podrías añadir lógica aquí para mensajes de texto que no son capturados por `general_message_handler`
            # si `general_message_handler` tuviera filtros más restrictivos, pero usualmente no es necesario.
    # application.add_handler(MessageHandler(filters.COMMAND, unknown_command_or_message_handler)) # Solo para comandos.
    # O para cualquier mensaje de texto no capturado antes:
    # application.add_handler(MessageHandler(filters.TEXT, unknown_command_or_message_handler)) # Cuidado con este, puede ser muy amplio.


    # --- 6. Inicio del Bot (Polling) ---
    logger.info("🤖 Bot configurado y listo. Iniciando polling...")
    
    # `run_polling` inicia el proceso de pedir actualizaciones a Telegram.
    # `allowed_updates=Update.ALL_TYPES` procesa todos los tipos de updates (mensajes, callbacks, etc.).
    # `drop_pending_updates=True` puede ser útil al reiniciar para ignorar mensajes viejos que llegaron mientras el bot estaba offline.
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES, 
            drop_pending_updates=True, # Considera True para desarrollo/pruebas, False para producción si no quieres perder updates.
            # timeout=30 # Timeout para el long polling (ya configurado en builder).
            # poll_interval=0.0 # Intervalo de polling (0.0 es el default, PTB lo maneja).
        )
    except KeyboardInterrupt:
        # Permite detener el bot limpiamente con Ctrl+C.
        logger.info("Polling detenido manualmente (KeyboardInterrupt).")
    except Exception as e:
        # Captura cualquier otra excepción crítica que pueda detener el polling.
        logger.critical(f"El bot se detuvo debido a un error crítico no manejado durante el polling: {e}", exc_info=True)
    finally:
        logger.info("============================================================")
        logger.info("🛑 BOT DETENIDO 🛑")
        logger.info("============================================================")

if __name__ == "__main__":
    # Este bloque se ejecuta cuando el script es llamado directamente (ej. `python main_bot.py`).
    
    # (Opcional) Carga de variables de entorno desde .env si no se hace globalmente en config.py.
    # from dotenv import load_dotenv
    # load_dotenv() # Asegura que se carguen antes de que config.py las use.
    
    main()

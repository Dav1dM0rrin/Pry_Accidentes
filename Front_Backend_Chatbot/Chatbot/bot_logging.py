# Archivo: chatbot/bot_logging.py
# Configuración del sistema de logging para la aplicación del chatbot.

import logging
import sys # Para acceder a stdout

# --- Nombre del Logger Principal de la Aplicación ---
# Usar un nombre específico para el logger de tu aplicación ayuda a evitar conflictos
# con loggers de librerías de terceros y permite una configuración más granular.
APP_LOGGER_NAME = "ChatbotVial"

# --- Obtener el Logger Principal ---
# Esta es la instancia del logger que otros módulos importarán y usarán.
logger = logging.getLogger(APP_LOGGER_NAME)

# --- Función de Configuración del Logging ---
def setup_logging(level_name: str = "INFO") -> None:
    """
    Configura el logging para la aplicación.

    Esta función debe ser llamada una sola vez al inicio de la aplicación
    (generalmente en main_bot.py) para establecer el formato, nivel y
    manejadores (handlers) para los mensajes de log.

    Args:
        level_name (str): El nivel de logging deseado como string (ej. "DEBUG", "INFO").
                          Por defecto es "INFO".
    """
    # Convertir el nombre del nivel (string) a su valor numérico correspondiente (int).
    # logging.getLevelName() puede tomar un string o un int.
    log_level_numeric = logging.getLevelName(level_name.upper())
    if not isinstance(log_level_numeric, int):
        # Si el nivel no es reconocido, usar INFO por defecto y advertir.
        print(f"ADVERTENCIA: Nivel de logging '{level_name}' no reconocido. Usando INFO por defecto.")
        log_level_numeric = logging.INFO

    # --- Configuración del Formato de los Mensajes de Log ---
    # Define cómo se verá cada línea de log.
    # Ejemplo: "2024-05-21 10:00:00,123 - ChatbotVial - INFO - Este es un mensaje de log"
    log_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S" # Formato de la fecha y hora.
    )

    # --- Configuración del Manejador (Handler) ---
    # Define a dónde se enviarán los mensajes de log.
    # Usaremos un StreamHandler para enviar los logs a la salida estándar (consola).
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter) # Aplicar el formato al handler.
    console_handler.setLevel(log_level_numeric) # Establecer el nivel para este handler.

    # --- Configuración del Logger Principal de la Aplicación ---
    # Limpiar handlers existentes para evitar duplicación si se llama múltiples veces (aunque no debería).
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler) # Añadir el handler configurado al logger.
    logger.setLevel(log_level_numeric) # Establecer el nivel para el logger principal.

    # Evitar que los mensajes se propaguen al logger raíz si no se desea.
    # logger.propagate = False # Descomentar si quieres control total y no heredar del root.

    # (Opcional) Configurar el logger raíz también, aunque es mejor configurar el logger específico de la app.
    # logging.basicConfig(level=log_level_numeric, format=log_formatter.format_string, handlers=[console_handler])

    logger.info(f"Logging configurado para '{APP_LOGGER_NAME}' con nivel {logging.getLevelName(logger.getEffectiveLevel())}.")

# --- Ejemplo de Uso (solo para probar este archivo directamente) ---
if __name__ == "__main__":
    # Esto solo se ejecuta si corres `python bot_logging.py` directamente.
    # En tu aplicación principal, llamarás a `setup_logging()` desde `main_bot.py`.
    
    print("Probando configuración de logging...")
    
    # Prueba con diferentes niveles.
    setup_logging(level_name="DEBUG") # Configura a DEBUG para ver todos los mensajes.
    logger.debug("Este es un mensaje de DEBUG.")
    logger.info("Este es un mensaje de INFO.")
    logger.warning("Este es un mensaje de WARNING.")
    logger.error("Este es un mensaje de ERROR.")
    logger.critical("Este es un mensaje CRITICAL.")

    print("\nProbando con nivel INFO...")
    setup_logging(level_name="INFO")
    logger.debug("Este mensaje DEBUG NO debería verse ahora.")
    logger.info("Este mensaje INFO SÍ debería verse.")

    print("\nPrueba de logger desde otro 'módulo' (simulado):")
    # Así es como otros módulos usarían el logger:
    # from chatbot.bot_logging import logger
    another_logger = logging.getLogger(APP_LOGGER_NAME) # Obtiene la misma instancia.
    another_logger.info("Mensaje de info desde 'otro_modulo' usando el mismo logger.")
    
    print(f"El logger '{logger.name}' tiene handlers: {logger.handlers}")

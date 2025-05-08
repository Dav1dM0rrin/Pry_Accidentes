import logging
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configura el logging para ver los mensajes de error
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Configuración ---
# Reemplaza con tu token de Telegram
YOUR_TELEGRAM_BOT_TOKEN = "8030993259:AAHXwtRUoDdhevv51BZ3U_s7NNgsmDwVm20"
# Reemplaza con la URL base de tu API
YOUR_API_BASE_URL = "http://127.0.0.1:8000" # Ejemplo: "http://localhost:8000"

# --- Handler para el comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje de bienvenida cuando se recibe el comando /start."""
    await update.message.reply_text('Hola! Soy un bot sobre accidentes en Barranquilla. Usa /ultimos10 para ver los accidentes más recientes.')

# --- Handler para el comando /ultimos10 ---
async def ultimos_10_accidentes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Obtiene y muestra los últimos 10 accidentes."""
    api_url = f"{YOUR_API_BASE_URL}/accidentes/"
    
    try:
        # Realiza la llamada a tu API
        response = requests.get(api_url)
        response.raise_for_status() # Lanza una excepción para códigos de estado de error (4xx o 5xx)
        
        accidentes = response.json() # Obtiene los datos como una lista de diccionarios
        
        if not accidentes:
            await update.message.reply_text("No hay accidentes registrados en la base de datos.")
            return

        # Ordenar accidentes por fecha de forma descendente
        # Asegúrate de que la fecha esté en un formato que Python pueda ordenar (datetime)
        # El formato de fecha en tu schema es 'datetime', lo cual es bueno.
        # Convertimos la cadena de fecha/hora a objeto datetime si viene como string
        for acc in accidentes:
             if isinstance(acc.get('fecha'), str):
                 # Intenta parsear la fecha. Asume formato ISO 8601, que FastAPI/Pydantic suelen usar.
                 try:
                     acc['fecha_dt'] = datetime.fromisoformat(acc['fecha'])
                 except ValueError:
                     logging.error(f"No se pudo parsear la fecha: {acc.get('fecha')}")
                     acc['fecha_dt'] = datetime.min # Asigna una fecha mínima si falla para no romper el ordenamiento

        # Filtra los que no se pudieron parsear o asigna una fecha muy antigua para que queden al final
        accidentes_validos = [acc for acc in accidentes if 'fecha_dt' in acc]

        # Ordena por el objeto datetime
        accidentes_ordenados = sorted(accidentes_validos, key=lambda x: x['fecha_dt'], reverse=True)

        # Tomar los últimos 10 (los primeros 10 después de ordenar de forma descendente)
        ultimos_10 = accidentes_ordenados[:10]

        # Formatear la respuesta
        mensaje = "Últimos 10 Accidentes:\n\n"
        for acc in ultimos_10:
            # Formato de la fecha más legible
            fecha_formateada = acc['fecha_dt'].strftime('%Y-%m-%d %H:%M') if 'fecha_dt' in acc else 'Fecha desconocida'
            
            # Aquí puedes añadir más detalles del accidente si la API los devuelve y son útiles
            # Por ahora, solo mostraremos ID y fecha
            mensaje += f"ID: {acc.get('id', 'N/A')}\n"
            mensaje += f"Fecha: {fecha_formateada}\n"
            # Puedes añadir más campos relevantes aquí (ej: tipo de accidente, ubicación - si los obtienes)
            # Ejemplo: mensaje += f"Tipo: {acc.get('tipo_accidente_nombre', 'Desconocido')}\n" 
            # NOTA: La API /accidentes/ actualmente no devuelve todos los detalles relacionados (ubicacion, tipo, etc.)
            # Si necesitas esos detalles, deberías considerar modificar tu API /accidentes/ para incluirlos o
            # usar el endpoint /accidentes/{id} para cada uno (menos eficiente).
            mensaje += "--------------------\n"

        await update.message.reply_text(mensaje)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error al llamar a la API: {e}")
        await update.message.reply_text("Lo siento, no pude comunicarme con la API de accidentes en este momento.")
    except Exception as e:
        logging.error(f"Ocurrió un error: {e}")
        await update.message.reply_text("Ocurrió un error inesperado al procesar tu solicitud.")


# --- Función principal para iniciar el bot ---
def main() -> None:
    """Inicia el bot de Telegram."""
    # Crea la aplicación del bot
    application = ApplicationBuilder().token(YOUR_TELEGRAM_BOT_TOKEN).build()

    # Registra los handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ultimos10", ultimos_10_accidentes))

    # Inicia el bot
    logging.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(poll_interval=3) # poll_interval en segundos

if __name__ == '__main__':
    main()
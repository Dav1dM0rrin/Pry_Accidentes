# chatbot/handlers/general.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

# Importa el servicio LLM y las funciones del api_client
from ..llm_service import get_intent_and_parameters
# --- CORRECCIÓN AQUÍ ---
# Importa la función con el nombre correcto: 'get_and_format_last_n_accidentes'
from ..api_client import get_and_format_last_n_accidentes#, get_accident_details # Importa otras funciones de api_client según las implementes

logger = logging.getLogger(__name__)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja mensajes de texto que no son comandos usando el LLM."""
    user_message = update.message.text
    user = update.effective_user
    logger.info(f"Mensaje de texto recibido de usuario {user.id} ({user.username or user.first_name}): '{user_message}'")

    # 1. Usar el LLM para identificar la intención y los parámetros
    intent_data = get_intent_and_parameters(user_message)

    intent = intent_data.get("intent")
    parameters = intent_data.get("parameters", {}) # Asegúrate de tener un diccionario de parámetros

    logger.info(f"LLM identificó intención: '{intent}' con parámetros: {parameters}")

    # 2. Actuar basado en la intención identificada
    reply_text = "Lo siento, no entendí tu solicitud. Intenta con /ultimos10 o formula tu pregunta de otra manera." # Mensaje por defecto

    if intent == "list_recent_accidents":
        # Llama a la lógica que obtiene y formatea los últimos 10 accidentes
        # Asegúrate de usar el nombre correcto de la función importada
        reply_text = get_and_format_last_n_accidentes(10) # Llama a la función corregida

    elif intent == "find_accident_by_id":
        accident_id = parameters.get("accident_id")
        if accident_id is not None:
            # Aquí llamarías a una función del api_client para buscar por ID
            # reply_text = get_accident_details(accident_id) # <-- Necesitas implementar esta función en api_client.py
            # Mientras no esté implementada:
            reply_text = f"Entendido, quieres buscar el accidente con ID {accident_id}. Esta función aún no está implementada."
        else:
            reply_text = "Parece que quieres buscar un accidente, pero no especificaste el ID."

    elif intent == "greet":
        # El LLM identificó un saludo o agradecimiento simple
        reply_text = f"¡Hola, {user.first_name}! ¿En qué puedo ayudarte hoy con los datos de accidentes?"
        # O un simple agradecimiento:
        # reply_text = "De nada. ¿Hay algo más en lo que pueda ayudarte?"

    elif intent == "error":
         reply_text = f"Ocurrió un error al procesar tu solicitud interna: {parameters.get('message', 'Error desconocido')}"

    # Si la intención es "unknown", se usa el mensaje de respuesta por defecto definido arriba.

    # 3. Enviar la respuesta al usuario
    await update.message.reply_text(reply_text)
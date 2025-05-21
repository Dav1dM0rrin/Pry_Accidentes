# Archivo: chatbot/handlers/general_handler.py
# Maneja mensajes de texto generales, interactuando con el servicio LLM.

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction # Para enviar acciones de chat como "typing..."

from chatbot.llm_service import (
    generate_response,
    classify_intent_and_extract_entities,
    reset_conversation_history
)
from chatbot.bot_logging import logger
from chatbot.api_client import get_accidents_from_api # Para la funcionalidad de RAG (consultar API).

# Podrías importar estados de conversación si este handler necesitara transicionar
# a un ConversationHandler específico, pero es más común que el LLM guíe al usuario
# a usar un comando que sea el entry_point de dicho ConversationHandler.
# from chatbot.handlers.conversation_states import REPORTING_ACCIDENT_DESCRIPTION


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja mensajes de texto generales del usuario.
    1. Clasifica la intención del mensaje.
    2. Si es una consulta que requiere datos de la API, los obtiene (RAG).
    3. Genera una respuesta conversacional usando el LLM con el contexto apropiado.
    """
    if not update.message or not update.message.text: # Ignorar mensajes vacíos o sin texto.
        logger.debug("GENERAL_HANDLER: Mensaje vacío o sin texto recibido, ignorando.")
        return

    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name or update.effective_user.username
    user_message = update.message.text.strip()

    if not user_message: # Ignorar si el mensaje queda vacío después de strip.
        logger.debug(f"GENERAL_HANDLER: Mensaje de user_id {user_id} quedó vacío después de strip, ignorando.")
        return

    logger.info(f"GENERAL_HANDLER: Mensaje recibido de user_id {user_id} ({user_name}): '{user_message}'")

    # Enviar acción de "typing..." para indicar que el bot está procesando.
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # --- Paso 1: Clasificar Intención y Extraer Entidades (Opcional pero Recomendado) ---
    # Esto ayuda a tomar decisiones más inteligentes antes de simplemente pasar todo al LLM.
    classification_result = await classify_intent_and_extract_entities(user_message)
    intent = classification_result.get("intent", "DESCONOCIDO")
    entities = classification_result.get("entities", {})
    
    logger.info(f"GENERAL_HANDLER: Intención clasificada para '{user_message}': {intent}. Entidades: {entities}")
    if classification_result.get("error"):
        logger.warning(f"GENERAL_HANDLER: Hubo un error en la clasificación de intención: {classification_result.get('error')}. Se procederá con LLM general.")
        # Si la clasificación falla críticamente, podrías tener un flujo de error o simplemente
        # dejar que el LLM general intente manejar el mensaje sin la info de intención/entidades.

    # --- Paso 2: Lógica basada en Intención (Ej. RAG para consultas) ---
    api_data_for_llm = None # Datos que se pasarán al LLM si se consulta la API.

    if intent == "CONSULTAR_ACCIDENTE":
        logger.info(f"GENERAL_HANDLER: Intención CONSULTAR_ACCIDENTE detectada. Entidades para API: {entities}")
        # Construir parámetros para la API basados en las entidades extraídas.
        # Esto requiere que tu API tenga filtros adecuados y que las entidades del LLM sean fiables.
        api_params = {}
        if "ubicacion" in entities and entities["ubicacion"]:
            # Asume que tu API puede filtrar por una subcadena en la dirección.
            api_params["direccion_aproximada_contiene"] = entities["ubicacion"]
        if "fecha" in entities and entities["fecha"]:
            # Parsear la fecha extraída por el LLM (ej. "hoy", "ayer", "20/05/2024")
            # a un formato que tu API entienda (ej. "YYYY-MM-DD").
            # Esta función `parse_fecha_flexible` necesitaría ser implementada.
            # parsed_date = await parse_fecha_flexible(entities["fecha"]) # Ejemplo
            # if parsed_date:
            #     api_params["fecha_ocurrencia_dia"] = parsed_date # Asume filtro por día.
            # Por simplicidad, si es "hoy", usamos la fecha actual.
            if entities["fecha"].lower() == "hoy":
                from datetime import date
                api_params["fecha_ocurrencia_dia"] = date.today().isoformat()
            else: # Para otras fechas, el LLM podría necesitar pedir formato específico o tu parseador ser muy bueno.
                logger.info(f"GENERAL_HANDLER: Fecha '{entities['fecha']}' requiere parseo avanzado no implementado para API.")


        if api_params: # Solo consultar la API si hay parámetros de filtro razonables.
            logger.info(f"GENERAL_HANDLER: Consultando API de accidentes con parámetros: {api_params}")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            api_response = await get_accidents_from_api(params=api_params)
            
            if isinstance(api_response, dict) and api_response.get("error"):
                logger.error(f"GENERAL_HANDLER: Error de API al consultar accidentes: {api_response.get('detail')}")
                # Informar al LLM del error para que pueda comunicarlo al usuario.
                api_data_for_llm = {"api_error_consulta": api_response.get('detail', 'Error al contactar la base de datos de accidentes.')}
            elif isinstance(api_response, list) and not api_response: # Lista vacía = no se encontraron.
                logger.info("GENERAL_HANDLER: No se encontraron accidentes en la API con los criterios dados.")
                api_data_for_llm = {"info_consulta": "No se encontraron accidentes que coincidan con tu búsqueda."}
            elif isinstance(api_response, list): # Se encontraron accidentes.
                 logger.info(f"GENERAL_HANDLER: {len(api_response)} accidentes encontrados en la API.")
                 api_data_for_llm = {"accidentes_encontrados": api_response} # Pasar la lista de accidentes al LLM.
            else: # Respuesta inesperada de la API
                logger.warning(f"GENERAL_HANDLER: Respuesta inesperada de la API de accidentes: {type(api_response)}")
                api_data_for_llm = {"info_consulta": "Hubo un problema al obtener datos de accidentes."}
        else:
            # Si no hay entidades suficientes para una búsqueda útil, el LLM debería pedir más detalles.
            # Esto se manejará en el prompt general del LLM.
            logger.info("GENERAL_HANDLER: No hay suficientes entidades para una consulta de API útil para CONSULTAR_ACCIDENTE.")
            # Podrías pasar una nota al LLM para que pida más información.
            api_data_for_llm = {"info_consulta": "Necesito más detalles para buscar accidentes, como una ubicación o fecha específica."}

    elif intent == "REPORTAR_ACCIDENTE":
        # Si el LLM detecta que el usuario quiere reportar un accidente,
        # el prompt de sistema del LLM (en `llm_service`) ya le indica que debe guiar al usuario
        # hacia el comando /reportar o empezar a recolectar información.
        # Si se extrajeron entidades, se pueden guardar en `context.user_data` para que
        # el `ConversationHandler` de `/reportar` las use si el usuario lo activa.
        if entities:
            context.user_data['llm_pre_extracted_report_entities'] = entities
            logger.info(f"GENERAL_HANDLER: Entidades para reporte pre-extraídas por LLM y guardadas en user_data: {entities}")
        # La respuesta la generará el LLM general, que ya tiene el contexto de "REPORTAR_ACCIDENTE" en su prompt.
        pass # Dejar que el LLM general maneje la respuesta guiando al usuario.

    # --- Paso 3: Generar la Respuesta Final con el LLM ---
    # `api_data_for_llm` contendrá los datos de la API (o errores/info) si la intención fue CONSULTAR_ACCIDENTE.
    # Para otras intenciones, será None, y el LLM responderá basado en su prompt de sistema y el historial.
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    final_llm_response_text = await generate_response(
        user_id,
        user_message,
        api_data_context=api_data_for_llm # Pasa los datos de la API (o None)
    )
    
    if final_llm_response_text:
        # Considera si quieres añadir botones de "acciones sugeridas" aquí basados en la respuesta del LLM.
        await update.message.reply_text(final_llm_response_text)
    else:
        # Fallback si el LLM no devuelve nada (poco probable si está bien configurado).
        logger.error(f"GENERAL_HANDLER: LLM no generó respuesta para el mensaje: '{user_message}' de user_id {user_id}")
        await update.message.reply_text("Lo siento, no pude procesar tu mensaje en este momento. Por favor, intenta de nuevo.")


async def reset_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /reset_chat para limpiar el historial de conversación del LLM para el usuario.
    """
    if not update.effective_user:
        logger.warning("RESET_CHAT: No se pudo obtener effective_user del update.")
        return

    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name or update.effective_user.username
    logger.info(f"RESET_CHAT: Comando /reset_chat recibido de user_id {user_id} ({user_name}).")

    if await reset_conversation_history(user_id):
        await update.message.reply_text(
            "He reseteado nuestro historial de conversación. 🧠✨\n"
            "¡Empecemos de nuevo! ¿En qué te puedo ayudar hoy?"
        )
    else:
        # Esto podría pasar si el bot se reinició y el historial en memoria se perdió,
        # o si es la primera interacción del usuario.
        await update.message.reply_text(
            "No había un historial previo que resetear, ¡así que estamos listos para empezar! 😊\n"
            "¿Cómo te puedo asistir?"
        )

# --- Definición del MessageHandler ---
# Este handler captura mensajes de texto que NO son comandos.
# El orden de registro en `main_bot.py` es importante: debe ir después de CommandHandlers y ConversationHandlers.
general_message_handler = MessageHandler(
    filters.UpdateType.MESSAGE & filters.TEXT & ~filters.COMMAND,
    handle_message
)


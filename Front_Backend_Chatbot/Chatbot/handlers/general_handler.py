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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja mensajes de texto generales del usuario.
    1. Clasifica la intención del mensaje.
    2. Si es una consulta que requiere datos de la API, los obtiene (RAG).
    3. Genera una respuesta conversacional usando el LLM con el contexto apropiado.
    """
    if not update.message or not update.message.text:
        logger.debug("GENERAL_HANDLER: Mensaje vacío o sin texto recibido, ignorando.")
        return

    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name or update.effective_user.username
    user_message = update.message.text.strip()

    if not user_message:
        logger.debug(f"GENERAL_HANDLER: Mensaje de user_id {user_id} quedó vacío después de strip, ignorando.")
        return

    logger.info(f"GENERAL_HANDLER: Mensaje recibido de user_id {user_id} ({user_name}): '{user_message}'")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    classification_result = await classify_intent_and_extract_entities(user_message)
    intent = classification_result.get("intent", "DESCONOCIDO")
    entities = classification_result.get("entities", {})
    
    logger.info(f"GENERAL_HANDLER: Intención clasificada para '{user_message}': {intent}. Entidades: {entities}")
    if classification_result.get("error"):
        logger.warning(f"GENERAL_HANDLER: Hubo un error en la clasificación de intención: {classification_result.get('error')}. Se procederá con LLM general.")

    api_data_for_llm = None

    if intent == "CONSULTAR_ACCIDENTE":
        logger.info(f"GENERAL_HANDLER: Intención CONSULTAR_ACCIDENTE detectada. Entidades para API: {entities}")
        api_params_for_request = {} # Cambiado el nombre de la variable local para claridad
        if "ubicacion" in entities and entities["ubicacion"]:
            api_params_for_request["direccion_aproximada_contiene"] = entities["ubicacion"]
        if "fecha" in entities and entities["fecha"]:
            if entities["fecha"].lower() == "hoy":
                from datetime import date
                api_params_for_request["fecha_ocurrencia_dia"] = date.today().isoformat()
            else:
                logger.info(f"GENERAL_HANDLER: Fecha '{entities['fecha']}' requiere parseo avanzado no implementado para API.")

        if api_params_for_request:
            logger.info(f"GENERAL_HANDLER: Consultando API de accidentes con parámetros: {api_params_for_request}")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            # CORREGIDO AQUÍ: Se llama con 'params='
            api_response = await get_accidents_from_api(params=api_params_for_request) 
            
            if isinstance(api_response, dict) and api_response.get("error"):
                logger.error(f"GENERAL_HANDLER: Error de API al consultar accidentes: {api_response.get('detail')}")
                api_data_for_llm = {"api_error_consulta": api_response.get('detail', 'Error al contactar la base de datos de accidentes.')}
            elif isinstance(api_response, list) and not api_response:
                logger.info("GENERAL_HANDLER: No se encontraron accidentes en la API con los criterios dados.")
                api_data_for_llm = {"info_consulta": "No se encontraron accidentes que coincidan con tu búsqueda."}
            elif isinstance(api_response, list):
                 logger.info(f"GENERAL_HANDLER: {len(api_response)} accidentes encontrados en la API.")
                 api_data_for_llm = {"accidentes_encontrados": api_response}
            else:
                logger.warning(f"GENERAL_HANDLER: Respuesta inesperada de la API de accidentes: {type(api_response)}")
                api_data_for_llm = {"info_consulta": "Hubo un problema al obtener datos de accidentes."}
        else:
            logger.info("GENERAL_HANDLER: No hay suficientes entidades para una consulta de API útil para CONSULTAR_ACCIDENTE.")
            api_data_for_llm = {"info_consulta": "Necesito más detalles para buscar accidentes, como una ubicación o fecha específica."}

    elif intent == "REPORTAR_ACCIDENTE":
        if entities:
            context.user_data['llm_pre_extracted_report_entities'] = entities
            logger.info(f"GENERAL_HANDLER: Entidades para reporte pre-extraídas por LLM y guardadas en user_data: {entities}")
        pass

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    final_llm_response_text = await generate_response(
        user_id,
        user_message,
        api_data_context=api_data_for_llm
    )
    
    if final_llm_response_text:
        await update.message.reply_text(final_llm_response_text)
    else:
        logger.error(f"GENERAL_HANDLER: LLM no generó respuesta para el mensaje: '{user_message}' de user_id {user_id}")
        await update.message.reply_text("Lo siento, no pude procesar tu mensaje en este momento. Por favor, intenta de nuevo.")

async def reset_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        await update.message.reply_text(
            "No había un historial previo que resetear, ¡así que estamos listos para empezar! 😊\n"
            "¿Cómo te puedo asistir?"
        )

general_message_handler = MessageHandler(
    filters.UpdateType.MESSAGE & filters.TEXT & ~filters.COMMAND,
    handle_message
)

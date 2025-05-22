# Archivo: chatbot/handlers/accident_handler.py
# Contiene el ConversationHandler para el flujo estructurado de reporte de accidentes
# y handlers para consulta de accidentes.

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from chatbot.bot_logging import logger
# Importar ambas funciones de api_client que ahora se usan en este handler
from chatbot.api_client import report_accident_api, get_accidente_by_id
from .conversation_states import ( 
    REPORTING_ACCIDENT_DESCRIPTION, REPORTING_ACCIDENT_LOCATION,
    REPORTING_ACCIDENT_DATETIME_CHOICE, REPORTING_ACCIDENT_DATETIME_SPECIFIC,
    REPORTING_ACCIDENT_GRAVEDAD, REPORTING_ACCIDENT_CONFIRMATION,
)
import datetime
from zoneinfo import ZoneInfo 
import re # Para expresiones regulares en el manejo de lenguaje natural
from typing import Optional, Dict, Any # Para type hints en las nuevas funciones

COLOMBIA_TZ = ZoneInfo("America/Bogota")

# --- Funciones del ConversationHandler para Reportar Accidente (TU CÓDIGO EXISTENTE) ---
# (Todo tu código para start_accident_report, accident_description_handler, 
# accident_location_handler, accident_datetime_choice_handler, 
# accident_datetime_specific_handler, ask_for_gravity_handler, 
# accident_gravity_handler, show_final_confirmation_handler, 
# accident_final_confirmation_handler, y cancel_report_handler 
# se mantiene aquí sin cambios. No lo repito para brevedad, pero asegúrate de que esté completo.)
async def start_accident_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.effective_user:
        logger.warning("ACCIDENT_HANDLER: start_accident_report sin effective_user.")
        return ConversationHandler.END 
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name or update.effective_user.username
    logger.info(f"ACCIDENT_HANDLER: Usuario {user_id} ({user_name}) inició reporte de accidente con /reportar.")
    context.user_data.pop('current_accident_report_data', None)
    pre_extracted_entities = context.user_data.pop('llm_pre_extracted_report_entities', None)
    current_report_data = {} 
    if pre_extracted_entities and isinstance(pre_extracted_entities, dict):
        logger.info(f"ACCIDENT_HANDLER: Usando entidades pre-extraídas por LLM: {pre_extracted_entities}")
        current_report_data['descripcion_llm'] = pre_extracted_entities.get('descripcion')
        current_report_data['ubicacion_texto_llm'] = pre_extracted_entities.get('ubicacion')
    context.user_data['current_accident_report_data'] = current_report_data
    if current_report_data.get('descripcion_llm'):
        await update.message.reply_text(
            f"He entendido que quieres reportar un accidente y mencionaste algo sobre: \"{current_report_data['descripcion_llm']}\".\n\n"
            "Para continuar, por favor, proporciona la **ubicación exacta** del accidente (ej: Calle 72 con Carrera 46, Barrio El Prado)."
            "\nTambién puedes compartir tu ubicación actual usando el botón de 'Compartir Ubicación' (ícono del clip 📎 en Telegram).",
            reply_markup=ReplyKeyboardRemove()
        )
        return REPORTING_ACCIDENT_LOCATION
    else:
        await update.message.reply_text(
            "Entendido. Vamos a reportar un accidente paso a paso.\n\n"
            "Primero, por favor, **describe brevemente qué sucedió** en el accidente.",
            reply_markup=ReplyKeyboardRemove()
        )
        return REPORTING_ACCIDENT_DESCRIPTION


async def accident_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    description_text = update.message.text.strip()
    if not description_text: 
        await update.message.reply_text("La descripción no puede estar vacía. Por favor, describe qué sucedió o usa /cancelar.")
        return REPORTING_ACCIDENT_DESCRIPTION

    report_data = context.user_data.get('current_accident_report_data', {})
    report_data['descripcion_usuario'] = description_text 
    context.user_data['current_accident_report_data'] = report_data
    logger.info(f"ACCIDENT_HANDLER: Descripción del accidente: '{description_text}' para user_id {update.effective_user.id}")

    pre_extracted_location_text = report_data.get('ubicacion_texto_llm')
    if pre_extracted_location_text:
        await update.message.reply_text(
            f"Gracias por la descripción.\n"
            f"El asistente entendió inicialmente que la ubicación podría ser \"{pre_extracted_location_text}\".\n"
            "¿Es esta la **ubicación correcta**? Puedes confirmarla escribiéndola de nuevo, corregirla, o compartir tu ubicación actual usando el botón de 'Compartir Ubicación' (ícono del clip 📎).",
        )
    else:
        await update.message.reply_text(
            f"Entendido. Descripción registrada.\n\n"
            "Ahora, por favor, indica la **ubicación exacta** del accidente (ej: Calle 72 con Carrera 46, Barrio Recreo)."
            "\nTambién puedes compartir tu ubicación actual usando el botón de 'Compartir Ubicación' (ícono del clip 📎).",
        )
    return REPORTING_ACCIDENT_LOCATION


async def accident_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_telegram_location = update.message.location 
    user_text_location = update.message.text.strip() if update.message.text else None 
    
    report_data = context.user_data.get('current_accident_report_data', {})
    location_display_text = "No especificada"

    if user_telegram_location:
        report_data['latitud_telegram'] = user_telegram_location.latitude
        report_data['longitud_telegram'] = user_telegram_location.longitude
        location_display_text = f"coordenadas (Lat: {user_telegram_location.latitude:.5f}, Lon: {user_telegram_location.longitude:.5f})"
        report_data['ubicacion_tipo_entrada'] = "coordenadas_telegram"
        logger.info(f"ACCIDENT_HANDLER: Ubicación del accidente (coordenadas Telegram): {location_display_text} para user_id {update.effective_user.id}")
    elif user_text_location:
        report_data['direccion_texto_usuario'] = user_text_location
        location_display_text = user_text_location
        report_data['ubicacion_tipo_entrada'] = "texto_usuario"
        report_data.pop('latitud_telegram', None)
        report_data.pop('longitud_telegram', None)
        logger.info(f"ACCIDENT_HANDLER: Ubicación del accidente (texto usuario): '{location_display_text}' para user_id {update.effective_user.id}")
    else: 
        await update.message.reply_text("No pude obtener la información de ubicación. Por favor, inténtalo de nuevo escribiendo la dirección o compartiendo tu ubicación, o usa /cancelar.")
        return REPORTING_ACCIDENT_LOCATION

    report_data['ubicacion_procesada_para_mostrar'] = location_display_text 
    context.user_data['current_accident_report_data'] = report_data 

    datetime_choice_keyboard = [
        [KeyboardButton("Sí, el accidente acaba de ocurrir")],
        [KeyboardButton("No, el accidente fue antes")]
    ]
    await update.message.reply_text(
        f"Ubicación registrada: \"{location_display_text}\".\n\n"
        "Ahora, sobre la **fecha y hora del accidente**: ¿Ocurrió justo ahora o en un momento anterior?",
        reply_markup=ReplyKeyboardMarkup(datetime_choice_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Elige una opción de fecha/hora"),
    )
    return REPORTING_ACCIDENT_DATETIME_CHOICE


async def accident_datetime_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice_text = update.message.text
    report_data = context.user_data.get('current_accident_report_data', {})

    if "Sí, el accidente acaba de ocurrir" in user_choice_text:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        report_data['fecha_hora_ocurrencia_iso'] = now_utc.isoformat() 
        logger.info(f"ACCIDENT_HANDLER: Fecha/hora del accidente: AHORA ({report_data['fecha_hora_ocurrencia_iso']}) para user_id {update.effective_user.id}")
        context.user_data['current_accident_report_data'] = report_data
        return await ask_for_gravity_handler(update, context) 
    elif "No, el accidente fue antes" in user_choice_text:
        await update.message.reply_text(
            "Entendido.\nPor favor, indica la **fecha y hora exactas** del accidente.\n"
            "Usa el formato: DD/MM/AAAA HH:MM (ejemplo: 21/05/2024 14:30).",
            reply_markup=ReplyKeyboardRemove(), 
        )
        return REPORTING_ACCIDENT_DATETIME_SPECIFIC 
    else: 
        await update.message.reply_text("Por favor, elige una de las opciones del teclado: 'Sí, el accidente acaba de ocurrir' o 'No, el accidente fue antes'.")
        return REPORTING_ACCIDENT_DATETIME_CHOICE


async def accident_datetime_specific_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    datetime_input_text = update.message.text.strip()
    report_data = context.user_data.get('current_accident_report_data', {})
    
    parsed_datetime_object = None
    formats_to_try = ["%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M"] 
    for fmt in formats_to_try:
        try:
            parsed_datetime_object = datetime.datetime.strptime(datetime_input_text, fmt)
            break 
        except ValueError:
            continue 
            
    if not parsed_datetime_object:
        logger.warning(f"ACCIDENT_HANDLER: Formato de fecha/hora inválido: '{datetime_input_text}' de user_id {update.effective_user.id}")
        await update.message.reply_text(
            "El formato de fecha/hora que ingresaste no es reconocido. 🤔\n"
            "Por favor, usa DD/MM/AAAA HH:MM (ejemplo: 21/05/2024 14:30).\n"
            "Si te equivocaste, puedes usar /cancelar y luego /reportar de nuevo para elegir la opción 'Sí, el accidente acaba de ocurrir'."
        )
        return REPORTING_ACCIDENT_DATETIME_SPECIFIC 
    
    if parsed_datetime_object.tzinfo is None:
        datetime_colombia_aware = COLOMBIA_TZ.localize(parsed_datetime_object)
    else: 
        datetime_colombia_aware = parsed_datetime_object.astimezone(COLOMBIA_TZ)
        
    report_data['fecha_hora_ocurrencia_iso'] = datetime_colombia_aware.isoformat()
    logger.info(f"ACCIDENT_HANDLER: Fecha/hora específica del accidente: {report_data['fecha_hora_ocurrencia_iso']} para user_id {update.effective_user.id}")
    context.user_data['current_accident_report_data'] = report_data
    return await ask_for_gravity_handler(update, context)


async def ask_for_gravity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    gravity_options_keyboard = [
        [KeyboardButton("LEVE (Solo daños materiales, sin heridos)")], 
        [KeyboardButton("MODERADA (Heridos leves, atención médica menor)")], 
        [KeyboardButton("GRAVE (Heridos graves, hospitalización o víctimas fatales)")]
    ]
    await update.message.reply_text(
        "Entendido. Ahora, por favor, indica cuál consideras que fue la **gravedad estimada** del accidente:",
        reply_markup=ReplyKeyboardMarkup(
            gravity_options_keyboard,
            one_time_keyboard=True, 
            resize_keyboard=True, 
            input_field_placeholder="Selecciona la gravedad del accidente"
        ),
    )
    return REPORTING_ACCIDENT_GRAVEDAD


async def accident_gravity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    gravity_choice_text = update.message.text
    report_data = context.user_data.get('current_accident_report_data', {})
    
    gravity_api_value = "LEVE" 
    if "LEVE" in gravity_choice_text.upper():
        gravity_api_value = "LEVE"
    elif "MODERADA" in gravity_choice_text.upper():
        gravity_api_value = "MODERADA"
    elif "GRAVE" in gravity_choice_text.upper() or "FATAL" in gravity_choice_text.upper():
        gravity_api_value = "GRAVE" 
    else:
        logger.warning(f"ACCIDENT_HANDLER: Gravedad no reconocida claramente de: '{gravity_choice_text}' para user_id {update.effective_user.id}. Usando LEVE por defecto.")
        await update.message.reply_text("No reconocí la opción de gravedad, se asignará 'LEVE'. Puedes corregir al final si es necesario.")

    report_data['gravedad_estimada_api'] = gravity_api_value
    report_data['gravedad_estimada_display'] = gravity_choice_text 
    logger.info(f"ACCIDENT_HANDLER: Gravedad estimada (API value): {gravity_api_value} para user_id {update.effective_user.id}")
    context.user_data['current_accident_report_data'] = report_data
    
    return await show_final_confirmation_handler(update, context)


async def show_final_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    report_data = context.user_data.get('current_accident_report_data', {})
    
    if not report_data or not report_data.get("descripcion_usuario"): 
        await update.message.reply_text(
            "Parece que no hemos recopilado suficiente información (falta la descripción).\n"
            "Por favor, inicia el reporte de nuevo con /reportar.", 
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    desc_display = report_data.get('descripcion_usuario', '_No especificada_')
    ubicacion_display = report_data.get('ubicacion_procesada_para_mostrar', '_No especificada_')
    fecha_hora_display = "_No especificada_"
    if 'fecha_hora_ocurrencia_iso' in report_data and report_data['fecha_hora_ocurrencia_iso']:
        try:
            dt_utc = datetime.datetime.fromisoformat(report_data['fecha_hora_ocurrencia_iso'])
            dt_colombia = dt_utc.astimezone(COLOMBIA_TZ)
            fecha_hora_display = dt_colombia.strftime("%d de %B de %Y a las %I:%M %p (%Z)") 
        except (ValueError, TypeError): 
            fecha_hora_display = str(report_data['fecha_hora_ocurrencia_iso']) 

    gravedad_display = report_data.get('gravedad_estimada_display', '_No especificada_')

    summary_message_parts = [
        "📝 *Resumen del Reporte de Accidente*",
        "Por favor, verifica cuidadosamente que toda la información sea correcta antes de enviar:\n",
        f"*Descripción*: {desc_display}",
        f"*Ubicación*: {ubicacion_display}",
        f"*Fecha y Hora*: {fecha_hora_display}",
        f"*Gravedad Estimada*: {gravedad_display}\n",
        "¿Es correcta esta información y deseas enviar el reporte ahora?"
    ]
    
    confirmation_keyboard_options = [
        [KeyboardButton("✅ Sí, enviar reporte ahora")],
        [KeyboardButton("❌ No, cancelar y corregir")]
    ]
    await update.message.reply_text(
        "\n".join(summary_message_parts),
        reply_markup=ReplyKeyboardMarkup(
            confirmation_keyboard_options,
            one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder="Confirma o cancela el reporte"
        ),
        parse_mode='Markdown' 
    )
    return REPORTING_ACCIDENT_CONFIRMATION


async def accident_final_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_final_choice = update.message.text
    report_data = context.user_data.get('current_accident_report_data', {})

    if "✅ Sí, enviar reporte ahora" in user_final_choice:
        if not report_data: 
            await update.message.reply_text("No hay datos de reporte para enviar. Por favor, usa /reportar de nuevo.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        api_payload = {
            "descripcion": report_data.get("descripcion_usuario"),
            "fecha_hora_ocurrencia": report_data.get("fecha_hora_ocurrencia_iso"), 
            "latitud": report_data.get("latitud_telegram"), 
            "longitud": report_data.get("longitud_telegram"), 
            "direccion_aproximada": report_data.get("direccion_texto_usuario", report_data.get("ubicacion_procesada_para_mostrar")),
            "ciudad": "Barranquilla", 
            "departamento": "Atlántico", 
            "gravedad_estimada": report_data.get("gravedad_estimada_api", "LEVE"), 
            "reportado_por_telegram_user_id": str(update.effective_user.id),
            "reportado_por_nombre": update.effective_user.full_name or update.effective_user.username,
        }
        
        payload_cleaned_for_api = {k: v for k, v in api_payload.items() if v is not None}

        logger.info(f"ACCIDENT_HANDLER: Enviando reporte final a la API: {payload_cleaned_for_api} para user_id {update.effective_user.id}")
        
        processing_msg = await update.message.reply_text("Procesando tu reporte, un momento por favor... 📡", reply_markup=ReplyKeyboardRemove())

        api_call_response = await report_accident_api(payload_cleaned_for_api) 

        if api_call_response and not api_call_response.get("error") and api_call_response.get("id_accidente"): 
            success_msg_text = (
                f"¡Excelente, {update.effective_user.first_name}! 👍\n"
                f"Tu reporte de accidente ha sido enviado y registrado con éxito.\n"
                f"El ID de tu reporte es: *{api_call_response.get('id_accidente')}*\n\n"
                "Gracias por tu colaboración para mejorar la seguridad vial en Barranquilla."
            )
            await context.bot.edit_message_text( 
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text=success_msg_text,
                parse_mode='Markdown'
            )
            logger.info(f"ACCIDENT_HANDLER: Reporte enviado exitosamente a la API. ID: {api_call_response.get('id_accidente')} para user_id {update.effective_user.id}")
        else:
            error_detail_from_api = "No se pudo procesar el reporte en el servidor."
            if isinstance(api_call_response, dict) and api_call_response.get("detail"):
                 error_detail_from_api = api_call_response.get("detail")
            
            error_msg_text = (
                f"Lo siento mucho, {update.effective_user.first_name}, pero parece que hubo un problema al enviar tu reporte al sistema:\n"
                f"_{error_detail_from_api}_\n\n"
                "Por favor, intenta de nuevo más tarde. Si el problema persiste, puedes contactar a soporte (si hay un canal definido)."
            )
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text=error_msg_text,
                parse_mode='Markdown'
            )
            logger.error(f"ACCIDENT_HANDLER: Error al enviar reporte a la API: {api_call_response} para user_id {update.effective_user.id}")

        context.user_data.pop('current_accident_report_data', None) 
        return ConversationHandler.END 
    
    elif "❌ No, cancelar y corregir" in user_final_choice:
        await update.message.reply_text(
            "Entendido. El reporte ha sido cancelado.\n"
            "Puedes iniciar uno nuevo con /reportar cuando quieras y proporcionar la información correcta desde el principio.",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.pop('current_accident_report_data', None)
        return ConversationHandler.END 
    else: 
        await update.message.reply_text("Por favor, elige '✅ Sí, enviar reporte ahora' o '❌ No, cancelar y corregir' usando los botones.")
        return REPORTING_ACCIDENT_CONFIRMATION


async def cancel_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"ACCIDENT_HANDLER: Usuario {user.full_name if user else 'Desconocido'} ({user.id if user else 'N/A'}) canceló el reporte de accidente con /cancelar.")
    context.user_data.pop('current_accident_report_data', None)
    context.user_data.pop('llm_pre_extracted_report_entities', None) 
    await update.message.reply_text(
        "El proceso de reporte de accidente ha sido cancelado.\n"
        "Si necesitas algo más, no dudes en preguntar o puedes iniciar de nuevo con /start o /ayuda.",
        reply_markup=ReplyKeyboardRemove(), 
    )
    return ConversationHandler.END 

# --- Definición del ConversationHandler para el Reporte de Accidentes (TU CÓDIGO EXISTENTE) ---
report_accident_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("reportar", start_accident_report)],
    states={
        REPORTING_ACCIDENT_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, accident_description_handler)
        ],
        REPORTING_ACCIDENT_LOCATION: [
            MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), accident_location_handler),
        ],
        REPORTING_ACCIDENT_DATETIME_CHOICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, accident_datetime_choice_handler)
        ],
        REPORTING_ACCIDENT_DATETIME_SPECIFIC: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, accident_datetime_specific_handler)
        ],
        REPORTING_ACCIDENT_GRAVEDAD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, accident_gravity_handler)
        ],
        REPORTING_ACCIDENT_CONFIRMATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, accident_final_confirmation_handler)
        ],
    },
    fallbacks=[
        CommandHandler("cancelar", cancel_report_handler),
        MessageHandler(filters.ALL, 
                       lambda update, context: update.message.reply_text(
                           "Hmm, no esperaba ese tipo de mensaje ahora. 🤔\n"
                           "Estamos en medio de un reporte de accidente. Por favor, sigue las instrucciones, "
                           "o usa /cancelar para salir del proceso de reporte."
                       ))
    ],
)

# --- NUEVAS FUNCIONES Y HANDLERS AÑADIDOS ABAJO PARA CONSULTAR DETALLES DE ACCIDENTE ---

# --- FUNCIÓN _format_accidente_details ACTUALIZADA ---
def _format_accidente_details(accidente_data: Optional[Dict[str, Any]]) -> str:
    """
    Formatea los datos del accidente para mostrarlos de forma legible al usuario.
    Args:
        accidente_data: Un diccionario con los datos del accidente o None.
    Returns:
        Un string formateado con los detalles del accidente.
    """
    if not accidente_data:
        return "No se pudo obtener la información del accidente o no se encontraron datos."

    # ID del accidente
    id_accidente = accidente_data.get('id', 'N/A') # El JSON de ejemplo usa 'id' para el accidente principal

    # Fecha y Hora
    fecha_hora_display = "No especificada"
    fecha_hora_iso = accidente_data.get('fecha') # El JSON de ejemplo usa 'fecha'
    if fecha_hora_iso:
        try:
            # Asumimos que la fecha viene en formato ISO 8601 como "2018-01-03T00:00:00"
            # Si no tiene zona horaria, la tratamos como UTC y la convertimos a Colombia
            dt_obj = datetime.datetime.fromisoformat(str(fecha_hora_iso).replace("Z", "+00:00"))
            if dt_obj.tzinfo is None: # Si es naive
                dt_utc = dt_obj.replace(tzinfo=datetime.timezone.utc) # Asumir UTC si es naive
            else:
                dt_utc = dt_obj.astimezone(datetime.timezone.utc) # Convertir a UTC si ya tiene tz
            
            dt_colombia = dt_utc.astimezone(COLOMBIA_TZ)
            fecha_hora_display = dt_colombia.strftime("%d de %B de %Y a las %I:%M %p (%Z)")
        except (ValueError, TypeError) as e:
            logger.error(f"Error al formatear fecha '{fecha_hora_iso}': {e}")
            fecha_hora_display = str(fecha_hora_iso) # Mostrar como está si no se puede parsear

    # Descripción (si tu API la devuelve, el JSON de ejemplo no la tiene directamente en el nivel superior)
    # Si la descripción está en otro lado o no existe para este endpoint, ajusta o elimina.
    descripcion_display = accidente_data.get('descripcion', 'No especificada por la API para este ID.')

    # Ubicación
    ubicacion_obj = accidente_data.get('ubicacion')
    ubicacion_display = "No especificada"
    if ubicacion_obj and isinstance(ubicacion_obj, dict):
        # Construir una dirección más completa si es posible
        # Ejemplo: "CALLE 27B con CARRERA 20B, Barrio Los Trupillos"
        via1_obj = ubicacion_obj.get('primer_via')
        via2_obj = ubicacion_obj.get('segunda_via')
        barrio_obj = ubicacion_obj.get('barrio')
        
        dir_parts = []
        if via1_obj and via1_obj.get('tipo_via', {}).get('nombre') and via1_obj.get('numero_via'):
            dir_parts.append(f"{via1_obj['tipo_via']['nombre']} {via1_obj['numero_via']}")
        if via2_obj and via2_obj.get('tipo_via', {}).get('nombre') and via2_obj.get('numero_via'):
            dir_parts.append(f"{via2_obj['tipo_via']['nombre']} {via2_obj['numero_via']}")
        
        direccion_vias = " con ".join(dir_parts) if len(dir_parts) == 2 else (dir_parts[0] if dir_parts else "")

        barrio_nombre = barrio_obj.get('nombre', '') if barrio_obj else ''
        
        if direccion_vias and barrio_nombre:
            ubicacion_display = f"{direccion_vias}, Barrio {barrio_nombre}"
        elif direccion_vias:
            ubicacion_display = direccion_vias
        elif barrio_nombre:
            ubicacion_display = f"Barrio {barrio_nombre}"
        
        complemento = ubicacion_obj.get('complemento')
        if complemento:
            ubicacion_display += f" ({complemento})"
        
        lat = ubicacion_obj.get('latitud')
        lon = ubicacion_obj.get('longitud')
        if lat is not None and lon is not None:
             ubicacion_display += f" (Lat: {lat:.5f}, Lon: {lon:.5f})"

    # Gravedad
    gravedad_obj = accidente_data.get('gravedad')
    gravedad_display = "No especificada"
    if gravedad_obj and isinstance(gravedad_obj, dict):
        gravedad_display = gravedad_obj.get('nivel_gravedad', 'No especificada')

    # Tipo de Accidente
    tipo_acc_obj = accidente_data.get('tipo_accidente')
    tipo_accidente_display = "No especificado"
    if tipo_acc_obj and isinstance(tipo_acc_obj, dict):
        tipo_accidente_display = tipo_acc_obj.get('nombre', 'No especificado')
        
    # Detalles de la víctima (del JSON de ejemplo)
    sexo_victima_display = accidente_data.get('sexo_victima', 'N/A')
    edad_victima_display = accidente_data.get('edad_victima', 'N/A')
    cantidad_victima_display = accidente_data.get('cantidad_victima', 'N/A')
    
    condicion_victima_obj = accidente_data.get('condicion_victima')
    condicion_victima_display = "No especificada"
    if condicion_victima_obj and isinstance(condicion_victima_obj, dict):
        condicion_victima_display = condicion_victima_obj.get('rol_victima', 'No especificada')

    # Usuario que reportó (si está disponible y es relevante mostrarlo)
    # usuario_obj = accidente_data.get('usuario')
    # reportado_por_display = "No especificado"
    # if usuario_obj and isinstance(usuario_obj, dict):
    #     reportado_por_display = usuario_obj.get('username', 'No especificado')

    details = [
        f"📄 *Detalles del Accidente (ID: {id_accidente})*",
        "-------------------------------------",
        f"🗓️ *Fecha y Hora*: {fecha_hora_display}",
        f"💥 *Tipo de Accidente*: {tipo_accidente_display}",
        f"📍 *Ubicación*: {ubicacion_display}",
        # f"📝 *Descripción (si aplica)*: {descripcion_display}", # Descomentar si tienes descripción
        f"📊 *Gravedad Víctima*: {gravedad_display}",
        f"👤 *Condición Víctima*: {condicion_victima_display}",
        f"🚻 *Sexo Víctima*: {sexo_victima_display}",
        f"🎂 *Edad Víctima*: {edad_victima_display}",
        f"🔢 *Cantidad de Víctimas en este registro*: {cantidad_victima_display}",
        # f"🗣️ Reportado por: {reportado_por_display}", # Descomentar si es relevante
    ]
    return "\n".join(details)

async def detalle_accidente_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el comando /detalle_accidente <ID> para obtener información de un accidente directamente.
    """
    user_id = update.effective_user.id
    logger.info(f"ACCIDENT_HANDLER: Usuario {user_id} ejecutó /detalle_accidente con args: {context.args}")

    if not context.args: 
        await update.message.reply_text(
            "Por favor, proporciona el ID del accidente después del comando.\n"
            "Ejemplo: `/detalle_accidente TU_ID_AQUI`",
            parse_mode='Markdown'
        )
        return

    accidente_id_input = context.args[0] 
    
    await update.message.reply_text(f"Buscando información para el accidente ID: `{accidente_id_input}`...", parse_mode='Markdown')
    
    accidente_info = await get_accidente_by_id(accidente_id_input) 

    if accidente_info:
        response_message = _format_accidente_details(accidente_info)
    else:
        response_message = f"No se encontró información para el accidente con ID: `{accidente_id_input}` o hubo un error al buscarlo."
    
    await update.message.reply_text(response_message, parse_mode='Markdown')

async def handle_natural_language_accident_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Intenta extraer un ID de accidente de un mensaje de texto normal (no un comando)
    y obtener su información. Este handler debe registrarse DESPUÉS de los CommandHandlers.
    """
    if not update.message or not update.message.text: 
        return
        
    message_text = update.message.text
    user_id = update.effective_user.id
    logger.info(f"ACCIDENT_HANDLER (Natural Language): Usuario {user_id} envió mensaje: '{message_text}'")
    
    id_patterns_with_keywords = [
        r"(?:detalle del accidente|informaci[oó]n del accidente|qu[eé] sabes del accidente|reporte del accidente|accidente|ver accidente)\s+([a-fA-F0-9]{1,24})", # ObjectId o ID numérico corto con keyword
        r"(?:detalle del accidente|informaci[oó]n del accidente|qu[eé] sabes del accidente|reporte del accidente|accidente|ver accidente)\s+(\d+)", 
    ]
    direct_id_patterns = [
        r"\b([a-fA-F0-9]{24})\b", 
        r"\b(\d{1,5})\b", # IDs numéricos de 1 a 5 dígitos (como el ID 12 de tu ejemplo)
    ]

    accidente_id_extracted = None

    for pattern_str in id_patterns_with_keywords:
        match = re.search(pattern_str, message_text, re.IGNORECASE)
        if match:
            accidente_id_extracted = match.group(1) 
            break
    
    if not accidente_id_extracted:
        for pattern_str in direct_id_patterns:
            match = re.search(pattern_str, message_text) 
            if match:
                accidente_id_extracted = match.group(1)
                break
    
    if accidente_id_extracted:
        accidente_id_extracted = accidente_id_extracted.strip() 
        logger.info(f"ACCIDENT_HANDLER (Natural Language): ID de accidente '{accidente_id_extracted}' extraído del mensaje: '{message_text}'")
        
        await update.message.reply_text(f"Detecté que podrías estar preguntando por el accidente ID: `{accidente_id_extracted}`. Permíteme buscarlo...", parse_mode='Markdown')
        
        accidente_info = await get_accidente_by_id(accidente_id_extracted)
        
        if accidente_info:
            response_message = _format_accidente_details(accidente_info)
        else:
            response_message = f"No pude encontrar información para el accidente con ID: `{accidente_id_extracted}`."
        
        await update.message.reply_text(response_message, parse_mode='Markdown')
        
    else:
        logger.info(f"ACCIDENT_HANDLER (Natural Language): No se detectó un ID de accidente claro en: '{message_text}'. El mensaje pasará a otros handlers.")

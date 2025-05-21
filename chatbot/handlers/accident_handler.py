# Archivo: chatbot/handlers/accident_handler.py
# Contiene el ConversationHandler para el flujo estructurado de reporte de accidentes.

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from chatbot.bot_logging import logger
from chatbot.api_client import report_accident_api # Para enviar el reporte final a la API.
from .conversation_states import ( # Definición de los estados de la conversación.
    REPORTING_ACCIDENT_DESCRIPTION, REPORTING_ACCIDENT_LOCATION,
    REPORTING_ACCIDENT_DATETIME_CHOICE, REPORTING_ACCIDENT_DATETIME_SPECIFIC,
    REPORTING_ACCIDENT_GRAVEDAD, REPORTING_ACCIDENT_CONFIRMATION,
    # SELECTING_ACTION # Podría ser un estado "padre" o de menú al que volver.
)
import datetime
from zoneinfo import ZoneInfo # Para manejo correcto de zonas horarias.

# Define la zona horaria de Colombia. Es importante para registrar fechas y horas correctamente.
COLOMBIA_TZ = ZoneInfo("America/Bogota")

# --- Funciones del ConversationHandler para Reportar Accidente ---

async def start_accident_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Punto de entrada para el ConversationHandler de reporte de accidentes.
    Se activa con el comando /reportar.
    """
    if not update.effective_user:
        logger.warning("ACCIDENT_HANDLER: start_accident_report sin effective_user.")
        return ConversationHandler.END # No se puede proceder sin usuario.

    user_id = update.effective_user.id
    user_name = update.effective_user.full_name or update.effective_user.username
    logger.info(f"ACCIDENT_HANDLER: Usuario {user_id} ({user_name}) inició reporte de accidente con /reportar.")
    
    # Limpiar datos de reportes anteriores de `user_data` para este flujo específico.
    context.user_data.pop('current_accident_report_data', None)
    
    # Verificar si hay entidades pre-extraídas por el LLM (desde general_handler).
    # Estas entidades se habrían guardado en `context.user_data['llm_pre_extracted_report_entities']`.
    pre_extracted_entities = context.user_data.pop('llm_pre_extracted_report_entities', None)
    
    current_report_data = {} # Iniciar un nuevo diccionario para este reporte.

    if pre_extracted_entities and isinstance(pre_extracted_entities, dict):
        logger.info(f"ACCIDENT_HANDLER: Usando entidades pre-extraídas por LLM para el reporte: {pre_extracted_entities}")
        # Mapear las entidades del LLM a los campos que este ConversationHandler espera.
        # Es importante que los nombres de las claves coincidan o se adapten.
        current_report_data['descripcion_llm'] = pre_extracted_entities.get('descripcion')
        current_report_data['ubicacion_texto_llm'] = pre_extracted_entities.get('ubicacion')
        # Parsear fecha y hora si el LLM las extrajo es más complejo y se podría hacer aquí
        # o dejar que el flujo normal del ConversationHandler las pida.
        # Ejemplo: current_report_data['fecha_hora_llm'] = parse_datetime_from_llm_entities(...)
    
    context.user_data['current_accident_report_data'] = current_report_data # Guardar en user_data.

    # Lógica para decidir el primer paso basado en si hay entidades pre-extraídas.
    if current_report_data.get('descripcion_llm'):
        # Si el LLM ya extrajo una descripción.
        await update.message.reply_text(
            f"He entendido que quieres reportar un accidente y mencionaste algo sobre: \"{current_report_data['descripcion_llm']}\".\n\n"
            "Para continuar, por favor, proporciona la **ubicación exacta** del accidente (ej: Calle 72 con Carrera 46, Barrio El Prado)."
            "\nTambién puedes compartir tu ubicación actual usando el botón de 'Compartir Ubicación' (ícono del clip 📎 en Telegram).",
            reply_markup=ReplyKeyboardRemove() # Quitar teclados anteriores.
        )
        return REPORTING_ACCIDENT_LOCATION # Saltar a pedir ubicación.
    else:
        # Si no hay descripción pre-extraída, empezar pidiéndola.
        await update.message.reply_text(
            "Entendido. Vamos a reportar un accidente paso a paso.\n\n"
            "Primero, por favor, **describe brevemente qué sucedió** en el accidente.",
            reply_markup=ReplyKeyboardRemove()
        )
        return REPORTING_ACCIDENT_DESCRIPTION # Estado inicial: pedir descripción.


async def accident_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la descripción del accidente y pide la ubicación."""
    description_text = update.message.text.strip()
    if not description_text: # Validar que no esté vacío.
        await update.message.reply_text("La descripción no puede estar vacía. Por favor, describe qué sucedió o usa /cancelar.")
        return REPORTING_ACCIDENT_DESCRIPTION

    report_data = context.user_data.get('current_accident_report_data', {})
    report_data['descripcion_usuario'] = description_text # Guardar descripción del usuario.
    context.user_data['current_accident_report_data'] = report_data
    logger.info(f"ACCIDENT_HANDLER: Descripción del accidente: '{description_text}' para user_id {update.effective_user.id}")

    # Verificar si la ubicación ya fue pre-extraída por LLM.
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
    return REPORTING_ACCIDENT_LOCATION # Siguiente estado: pedir ubicación.


async def accident_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la ubicación (texto o coordenadas de Telegram) y pide la elección de fecha/hora."""
    user_telegram_location = update.message.location # Objeto Location si el usuario comparte ubicación.
    user_text_location = update.message.text.strip() if update.message.text else None # Texto ingresado.
    
    report_data = context.user_data.get('current_accident_report_data', {})
    location_display_text = "No especificada"

    if user_telegram_location:
        report_data['latitud_telegram'] = user_telegram_location.latitude
        report_data['longitud_telegram'] = user_telegram_location.longitude
        # Podrías intentar obtener una dirección con geocodificación inversa aquí si lo deseas:
        # report_data['direccion_geocodificada'] = await geocode_reverse(user_telegram_location.latitude, user_telegram_location.longitude)
        location_display_text = f"coordenadas (Lat: {user_telegram_location.latitude:.5f}, Lon: {user_telegram_location.longitude:.5f})"
        report_data['ubicacion_tipo_entrada'] = "coordenadas_telegram"
        logger.info(f"ACCIDENT_HANDLER: Ubicación del accidente (coordenadas Telegram): {location_display_text} para user_id {update.effective_user.id}")
    elif user_text_location:
        report_data['direccion_texto_usuario'] = user_text_location
        location_display_text = user_text_location
        report_data['ubicacion_tipo_entrada'] = "texto_usuario"
        # Limpiar lat/lon si previamente se habían establecido por error y ahora se da texto.
        report_data.pop('latitud_telegram', None)
        report_data.pop('longitud_telegram', None)
        logger.info(f"ACCIDENT_HANDLER: Ubicación del accidente (texto usuario): '{location_display_text}' para user_id {update.effective_user.id}")
    else: 
        # Esto no debería ocurrir si los filtros del MessageHandler son correctos (texto O ubicación).
        await update.message.reply_text("No pude obtener la información de ubicación. Por favor, inténtalo de nuevo escribiendo la dirección o compartiendo tu ubicación, o usa /cancelar.")
        return REPORTING_ACCIDENT_LOCATION # Permanecer en el mismo estado.

    report_data['ubicacion_procesada_para_mostrar'] = location_display_text # Guardar lo que se procesó.
    context.user_data['current_accident_report_data'] = report_data # Actualizar user_data.

    # Teclado con opciones para la fecha/hora.
    datetime_choice_keyboard = [
        [KeyboardButton("Sí, el accidente acaba de ocurrir")],
        [KeyboardButton("No, el accidente fue antes")]
    ]
    await update.message.reply_text(
        f"Ubicación registrada: \"{location_display_text}\".\n\n"
        "Ahora, sobre la **fecha y hora del accidente**: ¿Ocurrió justo ahora o en un momento anterior?",
        reply_markup=ReplyKeyboardMarkup(datetime_choice_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Elige una opción de fecha/hora"),
    )
    return REPORTING_ACCIDENT_DATETIME_CHOICE # Siguiente estado.


async def accident_datetime_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la elección de si el accidente fue "ahora" o "antes", y avanza al siguiente paso."""
    user_choice_text = update.message.text
    report_data = context.user_data.get('current_accident_report_data', {})

    if "Sí, el accidente acaba de ocurrir" in user_choice_text:
        # Registrar la hora actual en UTC, luego se puede localizar o formatear.
        # Es mejor guardar en UTC y convertir para mostrar o para la API si requiere zona específica.
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        report_data['fecha_hora_ocurrencia_iso'] = now_utc.isoformat() # Guardar en formato ISO 8601 (UTC por defecto).
        logger.info(f"ACCIDENT_HANDLER: Fecha/hora del accidente: AHORA ({report_data['fecha_hora_ocurrencia_iso']}) para user_id {update.effective_user.id}")
        context.user_data['current_accident_report_data'] = report_data
        return await ask_for_gravity_handler(update, context) # Avanzar a preguntar gravedad.
    elif "No, el accidente fue antes" in user_choice_text:
        await update.message.reply_text(
            "Entendido.\nPor favor, indica la **fecha y hora exactas** del accidente.\n"
            "Usa el formato: DD/MM/AAAA HH:MM (ejemplo: 21/05/2024 14:30).",
            reply_markup=ReplyKeyboardRemove(), # Quitar teclado anterior.
        )
        return REPORTING_ACCIDENT_DATETIME_SPECIFIC # Estado para ingresar fecha/hora específica.
    else: # Respuesta inesperada.
        await update.message.reply_text("Por favor, elige una de las opciones del teclado: 'Sí, el accidente acaba de ocurrir' o 'No, el accidente fue antes'.")
        return REPORTING_ACCIDENT_DATETIME_CHOICE # Permanecer en el mismo estado.


async def accident_datetime_specific_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la fecha y hora específica ingresada por el usuario."""
    datetime_input_text = update.message.text.strip()
    report_data = context.user_data.get('current_accident_report_data', {})
    
    parsed_datetime_object = None
    # Intentar parsear formatos comunes. Puedes hacer esto más robusto o usar librerías como `dateutil`.
    formats_to_try = ["%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M"] # Añade más formatos si es necesario.
    for fmt in formats_to_try:
        try:
            parsed_datetime_object = datetime.datetime.strptime(datetime_input_text, fmt)
            break # Si se parsea correctamente, salir del bucle.
        except ValueError:
            continue # Intentar el siguiente formato.
            
    if not parsed_datetime_object:
        logger.warning(f"ACCIDENT_HANDLER: Formato de fecha/hora inválido: '{datetime_input_text}' de user_id {update.effective_user.id}")
        await update.message.reply_text(
            "El formato de fecha/hora que ingresaste no es reconocido. 🤔\n"
            "Por favor, usa DD/MM/AAAA HH:MM (ejemplo: 21/05/2024 14:30).\n"
            "Si te equivocaste, puedes usar /cancelar y luego /reportar de nuevo para elegir la opción 'Sí, el accidente acaba de ocurrir'."
        )
        return REPORTING_ACCIDENT_DATETIME_SPECIFIC # Permanecer en este estado para que el usuario reintente.
    
    # Asigna la zona horaria de Colombia al objeto datetime si es "naive" (no tiene tzinfo).
    # Si ya tiene tzinfo, es mejor convertirlo explícitamente a la zona horaria de Colombia.
    if parsed_datetime_object.tzinfo is None:
        datetime_colombia_aware = COLOMBIA_TZ.localize(parsed_datetime_object)
    else: # Si ya tiene timezone, convertir a la de Colombia.
        datetime_colombia_aware = parsed_datetime_object.astimezone(COLOMBIA_TZ)
        
    # Guardar en formato ISO 8601. Este formato incluye la información de timezone.
    report_data['fecha_hora_ocurrencia_iso'] = datetime_colombia_aware.isoformat()
    logger.info(f"ACCIDENT_HANDLER: Fecha/hora específica del accidente: {report_data['fecha_hora_ocurrencia_iso']} para user_id {update.effective_user.id}")
    context.user_data['current_accident_report_data'] = report_data
    return await ask_for_gravity_handler(update, context) # Avanzar a preguntar gravedad.


async def ask_for_gravity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pregunta por la gravedad estimada del accidente al usuario."""
    # Opciones de gravedad que se presentarán al usuario.
    # Estas deben ser claras y fáciles de entender.
    gravity_options_keyboard = [
        [KeyboardButton("LEVE (Solo daños materiales, sin heridos)")], 
        [KeyboardButton("MODERADA (Heridos leves, atención médica menor)")], 
        [KeyboardButton("GRAVE (Heridos graves, hospitalización o víctimas fatales)")]
    ]
    await update.message.reply_text(
        "Entendido. Ahora, por favor, indica cuál consideras que fue la **gravedad estimada** del accidente:",
        reply_markup=ReplyKeyboardMarkup(
            gravity_options_keyboard,
            one_time_keyboard=True, # El teclado desaparece después de una selección.
            resize_keyboard=True, # Ajusta el tamaño del teclado.
            input_field_placeholder="Selecciona la gravedad del accidente"
        ),
    )
    return REPORTING_ACCIDENT_GRAVEDAD # Siguiente estado: esperar la respuesta de gravedad.


async def accident_gravity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la gravedad estimada y avanza para mostrar la confirmación final."""
    gravity_choice_text = update.message.text
    report_data = context.user_data.get('current_accident_report_data', {})
    
    # Mapear el texto amigable de la opción elegida por el usuario a los valores que espera tu API
    # (ej. "LEVE", "MODERADA", "GRAVE").
    # Asegúrate que estos valores coincidan con los Enum o tipos permitidos en tu backend.
    gravity_api_value = "LEVE" # Valor por defecto si no se reconoce la opción.
    if "LEVE" in gravity_choice_text.upper():
        gravity_api_value = "LEVE"
    elif "MODERADA" in gravity_choice_text.upper():
        gravity_api_value = "MODERADA"
    elif "GRAVE" in gravity_choice_text.upper() or "FATAL" in gravity_choice_text.upper():
        # Considera si "FATAL" debe ser un valor separado en tu API o si se agrupa con "GRAVE".
        gravity_api_value = "GRAVE" 
    else:
        logger.warning(f"ACCIDENT_HANDLER: Gravedad no reconocida claramente de: '{gravity_choice_text}' para user_id {update.effective_user.id}. Usando LEVE por defecto.")
        # Podrías pedir de nuevo si no es claro, pero por ahora asignamos un default.
        await update.message.reply_text("No reconocí la opción de gravedad, se asignará 'LEVE'. Puedes corregir al final si es necesario.")


    report_data['gravedad_estimada_api'] = gravity_api_value
    report_data['gravedad_estimada_display'] = gravity_choice_text # Guardar también lo que el usuario vio/eligió.
    logger.info(f"ACCIDENT_HANDLER: Gravedad estimada (API value): {gravity_api_value} para user_id {update.effective_user.id}")
    context.user_data['current_accident_report_data'] = report_data
    
    return await show_final_confirmation_handler(update, context) # Mostrar resumen para confirmar.


async def show_final_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Muestra toda la información recopilada y pide confirmación final al usuario antes de enviar a la API."""
    report_data = context.user_data.get('current_accident_report_data', {})
    
    # Validar que se haya recopilado información esencial.
    if not report_data or not report_data.get("descripcion_usuario"): 
        await update.message.reply_text(
            "Parece que no hemos recopilado suficiente información (falta la descripción).\n"
            "Por favor, inicia el reporte de nuevo con /reportar.", 
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END # Terminar la conversación si faltan datos clave.

    # --- Formatear los datos para una presentación clara al usuario ---
    desc_display = report_data.get('descripcion_usuario', '_No especificada_')
    
    ubicacion_display = report_data.get('ubicacion_procesada_para_mostrar', '_No especificada_')
    
    fecha_hora_display = "_No especificada_"
    if 'fecha_hora_ocurrencia_iso' in report_data and report_data['fecha_hora_ocurrencia_iso']:
        try:
            # Convertir de ISO UTC a la zona horaria de Colombia para mostrar.
            dt_utc = datetime.datetime.fromisoformat(report_data['fecha_hora_ocurrencia_iso'])
            dt_colombia = dt_utc.astimezone(COLOMBIA_TZ)
            # Formato amigable para Colombia (ej: 21 de Mayo de 2024 a las 02:30 PM (COT))
            fecha_hora_display = dt_colombia.strftime("%d de %B de %Y a las %I:%M %p (%Z)") 
        except (ValueError, TypeError): # Si el string no es ISO o es None.
            fecha_hora_display = str(report_data['fecha_hora_ocurrencia_iso']) # Mostrar como está.

    gravedad_display = report_data.get('gravedad_estimada_display', '_No especificada_')

    # Construir el mensaje de resumen. Usar Markdown para formato.
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
        parse_mode='Markdown' # Habilitar Markdown para negritas, etc.
    )
    return REPORTING_ACCIDENT_CONFIRMATION # Estado final de confirmación.


async def accident_final_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la confirmación final del usuario.
    Si confirma, envía el reporte a la API. Si no, permite cancelar/corregir (actualmente solo cancela).
    """
    user_final_choice = update.message.text
    report_data = context.user_data.get('current_accident_report_data', {})

    if "✅ Sí, enviar reporte ahora" in user_final_choice:
        if not report_data: # Doble chequeo de seguridad.
            await update.message.reply_text("No hay datos de reporte para enviar. Por favor, usa /reportar de nuevo.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        # --- Preparar el payload final para enviar a la API ---
        # Asegúrate que los nombres de los campos coincidan con tu esquema Pydantic `AccidenteCreate` del backend.
        api_payload = {
            "descripcion": report_data.get("descripcion_usuario"),
            "fecha_hora_ocurrencia": report_data.get("fecha_hora_ocurrencia_iso"), # Debe ser ISO 8601 UTC.
            "latitud": report_data.get("latitud_telegram"), # Puede ser None si se dio dirección textual.
            "longitud": report_data.get("longitud_telegram"), # Puede ser None.
            "direccion_aproximada": report_data.get("direccion_texto_usuario", report_data.get("ubicacion_procesada_para_mostrar")),
            "ciudad": "Barranquilla", # Puedes hacerlo configurable o detectarlo si tu app es multi-ciudad.
            "departamento": "Atlántico", # Configurable.
            "gravedad_estimada": report_data.get("gravedad_estimada_api", "LEVE"), # Default si no se especificó.
            "reportado_por_telegram_user_id": str(update.effective_user.id),
            "reportado_por_nombre": update.effective_user.full_name or update.effective_user.username,
            # Añade otros campos que tu API requiera (ej. tipo_vehiculo_implicado, causa_probable, etc. si los recolectas).
        }
        
        # Limpiar el payload de claves con valor None si tu API no los espera o los maneja mal.
        # Pydantic usualmente maneja bien los `Optional[type] = None` no enviados.
        payload_cleaned_for_api = {k: v for k, v in api_payload.items() if v is not None}

        logger.info(f"ACCIDENT_HANDLER: Enviando reporte final a la API: {payload_cleaned_for_api} para user_id {update.effective_user.id}")
        
        # Mostrar un mensaje de "procesando..." al usuario.
        processing_msg = await update.message.reply_text("Procesando tu reporte, un momento por favor... 📡", reply_markup=ReplyKeyboardRemove())

        # Llamada a tu cliente API para enviar el reporte.
        api_call_response = await report_accident_api(payload_cleaned_for_api) 

        # --- Manejar la respuesta de la API ---
        if api_call_response and not api_call_response.get("error") and api_call_response.get("id_accidente"): 
            # Éxito: la API devolvió un ID de accidente y no marcó error.
            # (Ajusta "id_accidente" al nombre del campo ID que tu API realmente devuelve).
            success_msg_text = (
                f"¡Excelente, {update.effective_user.first_name}! 👍\n"
                f"Tu reporte de accidente ha sido enviado y registrado con éxito.\n"
                f"El ID de tu reporte es: *{api_call_response.get('id_accidente')}*\n\n"
                "Gracias por tu colaboración para mejorar la seguridad vial en Barranquilla."
            )
            await context.bot.edit_message_text( # Editar el mensaje "procesando..."
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text=success_msg_text,
                parse_mode='Markdown'
            )
            logger.info(f"ACCIDENT_HANDLER: Reporte enviado exitosamente a la API. ID: {api_call_response.get('id_accidente')} para user_id {update.effective_user.id}")
        else:
            # Fallo: la API marcó error o no devolvió la estructura esperada.
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

        # Limpiar datos del reporte de `user_data` después de intentar enviar.
        context.user_data.pop('current_accident_report_data', None) 
        return ConversationHandler.END # Terminar la conversación.
    
    elif "❌ No, cancelar y corregir" in user_final_choice:
        await update.message.reply_text(
            "Entendido. El reporte ha sido cancelado.\n"
            "Puedes iniciar uno nuevo con /reportar cuando quieras y proporcionar la información correcta desde el principio.",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.pop('current_accident_report_data', None)
        return ConversationHandler.END # Terminar la conversación.
    else: # Respuesta inesperada en la pantalla de confirmación.
        await update.message.reply_text("Por favor, elige '✅ Sí, enviar reporte ahora' o '❌ No, cancelar y corregir' usando los botones.")
        return REPORTING_ACCIDENT_CONFIRMATION # Permanecer en el estado de confirmación.


async def cancel_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Manejador para el comando /cancelar. Permite al usuario salir del flujo de reporte
    de accidente en cualquier punto.
    """
    user = update.effective_user
    logger.info(f"ACCIDENT_HANDLER: Usuario {user.full_name if user else 'Desconocido'} ({user.id if user else 'N/A'}) canceló el reporte de accidente con /cancelar.")
    
    # Limpiar cualquier dato de reporte en curso de `user_data`.
    context.user_data.pop('current_accident_report_data', None)
    context.user_data.pop('llm_pre_extracted_report_entities', None) # Limpiar también pre-extraídos.
    
    await update.message.reply_text(
        "El proceso de reporte de accidente ha sido cancelado.\n"
        "Si necesitas algo más, no dudes en preguntar o puedes iniciar de nuevo con /start o /ayuda.",
        reply_markup=ReplyKeyboardRemove(), # Quitar cualquier teclado custom.
    )
    return ConversationHandler.END # Finaliza el ConversationHandler.

# --- Definición del ConversationHandler para el Reporte de Accidentes ---
report_accident_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("reportar", start_accident_report)],
    states={
        REPORTING_ACCIDENT_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, accident_description_handler)
        ],
        REPORTING_ACCIDENT_LOCATION: [
            # Acepta tanto mensajes de texto (para direcciones) como objetos de ubicación de Telegram.
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
        # (Opcional) Un fallback genérico para mensajes inesperados dentro de esta conversación.
        MessageHandler(filters.ALL, # Captura cualquier tipo de mensaje no manejado por los estados.
                       lambda update, context: update.message.reply_text(
                           "Hmm, no esperaba ese tipo de mensaje ahora. 🤔\n"
                           "Estamos en medio de un reporte de accidente. Por favor, sigue las instrucciones, "
                           "o usa /cancelar para salir del proceso de reporte."
                       ))
    ],
    # Opcional: Configuración de persistencia si usas almacenamiento para conversaciones (ej. PicklePersistence).
    # persistent=False, # True si quieres que la conversación sobreviva reinicios del bot (requiere setup).
    # name="accident_report_conversation", # Nombre para la persistencia.

    # Opcional: Si quieres que al finalizar este ConversationHandler se pase a otro estado "padre" o menú.
    # map_to_parent={ 
    #     ConversationHandler.END: SELECTING_ACTION # Si SELECTING_ACTION es un estado de un ConvHandler padre.
    # } # Si no, ConversationHandler.END simplemente termina este flujo.
)

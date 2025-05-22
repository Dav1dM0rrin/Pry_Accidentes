# Archivo: chatbot/handlers/accident_handler.py

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from chatbot.bot_logging import logger
from chatbot.api_client import report_accident_api, get_accidente_by_id # Asumimos que get_accidente_by_id existe
from .conversation_states import ( # Asegúrate que estos estados coincidan con tu archivo conversation_states.py
    REPORTING_ACCIDENT_DATETIME_CHOICE, REPORTING_VICTIM_SEX,
    REPORTING_VICTIM_AGE, REPORTING_VICTIM_COUNT,
    REPORTING_VICTIM_CONDITION, REPORTING_ACCIDENT_GRAVITY,
    REPORTING_ACCIDENT_TYPE, REPORTING_BARRIO_SELECTION, 
    REPORTING_ACCIDENT_CONFIRMATION
)
import datetime
from zoneinfo import ZoneInfo
import re
from typing import Optional, Dict, Any

COLOMBIA_TZ = ZoneInfo("America/Bogota")

# --- Opciones predefinidas basadas en tu BD (idealmente, obtenerlas de la API) ---
CONDICION_VICTIMA_OPTIONS = {
    "Peatón": 1, "Pasajero": 2, "Acompañante": 3,
    "Conductor": 4, "Ciclista": 5, "Motociclista": 6
}
GRAVEDAD_VICTIMA_OPTIONS = { "Herido": 1, "Muerto": 2 }
TIPO_ACCIDENTE_OPTIONS = {
    "Choque": 1, "Atropello": 2, "Volcamiento": 3,
    "Caída Ocupante": 4, "Incendio": 5, "Otro": 6
}

# Extraído del SQL: tabla accidente_barrio
BARRIO_OPTIONS = {
    "El Prado": 1, "Alto Prado": 2, "Villa Country": 3, "Riomar": 4,
    "El Golf": 5, "Ciudad Jardín": 6, "Paraíso": 7, "Villa Santos": 8,
    "El Limoncito": 9, "Andalucía": 10, "Betania": 11, "El Recreo": 12,
    "Boston": 13, "Villa Carolina": 14, "El Porvenir": 15, "Modelo": 16,
    "Santa Ana": 17, "Monte Cristo": 18, "Chiquinquirá": 19, "San Roque": 20,
    "Rebolo": 21, "La Luz": 22, "Las Nieves": 23, "Simón Bolívar": 24,
    "Los Andes": 25, "La Victoria": 26, "El Santuario": 27, "La Sierra": 28,
    "El Bosque": 29, "Las Malvinas": 30, "La Paz": 31, "El Pueblo": 32,
    "Lipaya": 33, "Siape": 34, "Las Flores": 35, "Adelita de Char": 36,
    "La Playa": 37, "El Ferry": 38, "Pasadena": 39, "San Salvador": 40,
    "Bellavista": 41, "La Concepción": 42, "Colombia": 43, "El Castillo": 44,
    "Miramar": 45, "Buenavista": 46, "Las Delicias": 47, "América": 48,
    "El Rosario": 49, "Centro": 50, "Barlovento": 51, "Villanueva": 52,
    "La Chinita": 53, "El Carmen": 54, "Kennedy": 55, "Olaya": 56,
    "El Valle": 57, "Los Continentes": 58, "Sourdís": 59, "La Manga": 60,
    "Me Quejo": 61, "Por Fin": 62, "Los Olivos": 63, "La Pradera": 64,
    "El Edén": 65, "Las Granjas": 66, "Santo Domingo de Guzmán": 67,
    "Ciudadela 20 de Julio": 68, "Villa San Pedro": 69, "Las Américas": 70,
    "7 de Abril": 71, "Los Girasoles": 72, "Carrizal": 73, "Buenos Aires": 74,
    "Villa Sevilla": 75, "Las Cayenas": 76, "El Romance": 77, "California": 78,
    "Cordialidad": 79, "Villa San Carlos": 80, "La Sierrita": 81, "Evaristo Sourdís": 82,
    "La Gloria": 83, "Villa Flor": 84, "El Silencio": 85, "La Libertad": 86,
    "Nueva Granada": 87, "San Felipe": 88, "Lucero": 89, "Carlos Meisel": 90,
    "Nueva Colombia": 91, "Cuchilla de Villate": 92, "El Tabor": 93, "La Cumbre": 94,
    "Los Nogales": 95, "Campo Alegre": 96, "Las Estrellas": 97, "El Limón": 98,
    "Villate": 99, "San Isidro": 100, "Alfonso López": 101, "Los Pinos": 102,
    "El Rubí": 103, "La Ceiba": 104, "La Esmeralda": 105, "El Milagro": 106,
    "Pumarejo": 107, "La Unión": 108, "Boyacá": 109, "Atlántico": 110,
    "Los Trupillos": 111, "La Magdalena": 112, "El Campito": 113, "Las Palmas": 114,
    "La Loma": 115, "San José": 116, "Moderno": 117, "Montes": 118,
    "San Nicolás": 119, "José Antonio Galán": 120, "Villa Blanca": 121,
    "El Parque": 122, "Las Terrazas": 123
}

# --- Funciones para el Flujo de Reporte de Accidente (Versión con Opciones) ---

async def start_accident_report_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada para el nuevo flujo de reporte de accidentes."""
    user_id_telegram = update.effective_user.id
    # TODO: En Parte 2, verificar aquí si el usuario está logueado.
    # logger.info(f"ACCIDENT_HANDLER_V2: Usuario {user_id_telegram} inició reporte. Verificando login...")
    # if not context.user_data.get('backend_user_id'): # Asumiendo que guardas el ID del backend aquí tras login
    #     await update.message.reply_text("Debes iniciar sesión para reportar un accidente. Usa /login primero.")
    #     return ConversationHandler.END

    logger.info(f"ACCIDENT_HANDLER_V2: Usuario {user_id_telegram} inició reporte de accidente con /reportar.")
    context.user_data['current_accident_report_v2_data'] = {} # Limpiar/iniciar datos para este reporte
    
    await update.message.reply_text(
        "Vamos a reportar un nuevo accidente. Por favor, sigue los pasos.\n\n"
        "Primero, ¿cuándo ocurrió el accidente? (ej: DD/MM/AAAA HH:MM, o escribe 'ahora')",
        reply_markup=ReplyKeyboardMarkup([["Ahora"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return REPORTING_ACCIDENT_DATETIME_CHOICE

async def handle_accident_datetime_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la elección de fecha/hora o la fecha/hora específica."""
    text = update.message.text.strip()
    report_data = context.user_data.get('current_accident_report_v2_data', {})

    if text.lower() == "ahora":
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        # Formato ISO 8601 con 'Z' para UTC, como en tu ejemplo de payload
        report_data['fecha'] = now_utc.isoformat(timespec='milliseconds').replace("+00:00", "Z")
        logger.info(f"ACCIDENT_HANDLER_V2: Fecha/hora: AHORA ({report_data['fecha']})")
    else:
        parsed_dt = None
        # Formatos a intentar, incluyendo con y sin segundos, y diferentes separadores
        formats_to_try = [
            "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",    "%d-%m-%Y %H:%M",    "%Y-%m-%d %H:%M",
            "%d/%m/%y %H:%M:%S", "%d-%m-%y %H:%M:%S",
            "%d/%m/%y %H:%M",    "%d-%m-%y %H:%M"
        ]
        for fmt in formats_to_try:
            try:
                parsed_dt = datetime.datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_dt: # Intentar parsear solo fecha si no se incluye hora
            date_formats_to_try = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]
            for fmt in date_formats_to_try:
                try:
                    parsed_date_only = datetime.datetime.strptime(text, fmt)
                    # Asumir medianoche (00:00:00) si solo se da la fecha
                    parsed_dt = datetime.datetime.combine(parsed_date_only.date(), datetime.time.min)
                    logger.info(f"ACCIDENT_HANDLER_V2: Solo fecha ingresada '{text}', asumiendo medianoche: {parsed_dt}")
                    break
                except ValueError:
                    continue

        if parsed_dt:
            # Asumir que la fecha/hora ingresada es en la zona horaria de Colombia
            if parsed_dt.tzinfo is None:
                datetime_colombia_aware = COLOMBIA_TZ.localize(parsed_dt)
            else: # Si ya tiene timezone, convertir a Colombia
                datetime_colombia_aware = parsed_dt.astimezone(COLOMBIA_TZ)
            
            # Convertir a UTC para el payload
            datetime_utc = datetime_colombia_aware.astimezone(datetime.timezone.utc)
            report_data['fecha'] = datetime_utc.isoformat(timespec='milliseconds').replace("+00:00", "Z")
            logger.info(f"ACCIDENT_HANDLER_V2: Fecha/hora específica (UTC): {report_data['fecha']}")
        else:
            await update.message.reply_text(
                "Formato de fecha/hora no reconocido. 🤔\nUsa DD/MM/AAAA HH:MM (ej: 21/05/2024 14:30) o escribe 'ahora'. Inténtalo de nuevo:",
                reply_markup=ReplyKeyboardMarkup([["Ahora"]], one_time_keyboard=True, resize_keyboard=True)
            )
            return REPORTING_ACCIDENT_DATETIME_CHOICE

    context.user_data['current_accident_report_v2_data'] = report_data
    sex_keyboard = [["Masculino (M)"], ["Femenino (F)"], ["Otro (O)"]]
    # Mostrar fecha en formato local para confirmación visual
    fecha_local_display = datetime.datetime.fromisoformat(report_data['fecha'].replace('Z', '+00:00')).astimezone(COLOMBIA_TZ).strftime('%d/%m/%Y %I:%M %p')
    await update.message.reply_text(
        f"Fecha y hora registradas: {fecha_local_display} (Colombia).\n\n"
        "Ahora, selecciona el sexo de la víctima principal:",
        reply_markup=ReplyKeyboardMarkup(sex_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return REPORTING_VICTIM_SEX

async def handle_victim_sex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección del sexo de la víctima."""
    sexo_input = update.message.text.strip().upper()
    sexo_enviar = "O" # Default a 'Otro' si no coincide
    if "MASCULINO" in sexo_input or sexo_input == "M":
        sexo_enviar = "M"
    elif "FEMENINO" in sexo_input or sexo_input == "F":
        sexo_enviar = "F"
    # El payload espera "string", así que "M", "F", "O" son válidos.
    # Si tu backend espera específicamente solo M o F y maneja "Otro" de forma diferente, ajusta.
    
    context.user_data['current_accident_report_v2_data']['sexo_victima'] = sexo_enviar
    logger.info(f"ACCIDENT_HANDLER_V2: Sexo víctima: {sexo_enviar}")
    await update.message.reply_text("Sexo registrado. Ahora, la edad de la víctima principal (en años, solo números):", reply_markup=ReplyKeyboardRemove())
    return REPORTING_VICTIM_AGE

async def handle_victim_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja el ingreso de la edad de la víctima."""
    try:
        edad = int(update.message.text.strip())
        if not (0 <= edad <= 120): # Un rango razonable para la edad
            raise ValueError("Edad fuera de rango (0-120).")
        context.user_data['current_accident_report_v2_data']['edad_victima'] = edad
        logger.info(f"ACCIDENT_HANDLER_V2: Edad víctima: {edad}")
        await update.message.reply_text("Edad registrada. ¿Cuántas víctimas hubo en total en este accidente? (solo números)")
        return REPORTING_VICTIM_COUNT
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido para la edad (ej: 30).")
        return REPORTING_VICTIM_AGE

async def handle_victim_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja el ingreso de la cantidad de víctimas."""
    try:
        cantidad = int(update.message.text.strip())
        if cantidad < 1: # Debe haber al menos una víctima para este flujo
            raise ValueError("La cantidad de víctimas debe ser al menos 1.")
        context.user_data['current_accident_report_v2_data']['cantidad_victima'] = cantidad
        logger.info(f"ACCIDENT_HANDLER_V2: Cantidad víctimas: {cantidad}")
        
        keyboard = [[KeyboardButton(text)] for text in CONDICION_VICTIMA_OPTIONS.keys()]
        await update.message.reply_text(
            "Cantidad registrada.\n"
            "Ahora, selecciona la condición de la víctima principal (ej. Peatón, Conductor):",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return REPORTING_VICTIM_CONDITION
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido para la cantidad (ej: 1).")
        return REPORTING_VICTIM_COUNT

async def handle_victim_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de la condición de la víctima."""
    selected_condition_text = update.message.text.strip()
    condition_id = CONDICION_VICTIMA_OPTIONS.get(selected_condition_text)

    if condition_id is None:
        await update.message.reply_text("Opción no válida. Por favor, selecciona una condición de la lista.")
        keyboard = [[KeyboardButton(text)] for text in CONDICION_VICTIMA_OPTIONS.keys()]
        await update.message.reply_text(
            "Selecciona la condición de la víctima principal:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return REPORTING_VICTIM_CONDITION

    context.user_data['current_accident_report_v2_data']['condicion_victima_id'] = condition_id
    logger.info(f"ACCIDENT_HANDLER_V2: Condición víctima ID: {condition_id} (seleccionado: '{selected_condition_text}')")
    
    keyboard = [[KeyboardButton(text)] for text in GRAVEDAD_VICTIMA_OPTIONS.keys()]
    await update.message.reply_text(
        "Condición registrada.\n"
        "Selecciona la gravedad de la víctima principal (ej. Herido, Muerto):",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return REPORTING_ACCIDENT_GRAVITY

async def handle_accident_gravity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de la gravedad del accidente/víctima."""
    selected_gravity_text = update.message.text.strip()
    gravity_id = GRAVEDAD_VICTIMA_OPTIONS.get(selected_gravity_text)

    if gravity_id is None:
        await update.message.reply_text("Opción no válida. Por favor, selecciona una gravedad de la lista.")
        keyboard = [[KeyboardButton(text)] for text in GRAVEDAD_VICTIMA_OPTIONS.keys()]
        await update.message.reply_text(
            "Selecciona la gravedad de la víctima principal:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return REPORTING_ACCIDENT_GRAVITY
        
    context.user_data['current_accident_report_v2_data']['gravedad_victima_id'] = gravity_id
    logger.info(f"ACCIDENT_HANDLER_V2: Gravedad víctima ID: {gravity_id} (seleccionado: '{selected_gravity_text}')")
    
    keyboard = [[KeyboardButton(text)] for text in TIPO_ACCIDENTE_OPTIONS.keys()]
    await update.message.reply_text(
        "Gravedad registrada.\n"
        "Selecciona el tipo de accidente (ej. Choque, Atropello):",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return REPORTING_ACCIDENT_TYPE

async def handle_accident_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección del tipo de accidente."""
    selected_type_text = update.message.text.strip()
    type_id = TIPO_ACCIDENTE_OPTIONS.get(selected_type_text)

    if type_id is None:
        await update.message.reply_text("Opción no válida. Por favor, selecciona un tipo de accidente de la lista.")
        keyboard = [[KeyboardButton(text)] for text in TIPO_ACCIDENTE_OPTIONS.keys()]
        await update.message.reply_text(
            "Selecciona el tipo de accidente:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return REPORTING_ACCIDENT_TYPE

    context.user_data['current_accident_report_v2_data']['tipo_accidente_id'] = type_id
    logger.info(f"ACCIDENT_HANDLER_V2: Tipo accidente ID: {type_id} (seleccionado: '{selected_type_text}')")
    
    barrio_keys = list(BARRIO_OPTIONS.keys())
    keyboard_barrios = []
    # Agrupar barrios para teclados manejables. Ejemplo: 2 columnas.
    # En una app real, considera InlineKeyboards con paginación para listas muy largas.
    temp_row = []
    for i, barrio_key in enumerate(barrio_keys):
        temp_row.append(KeyboardButton(barrio_key))
        if len(temp_row) == 2 or i == len(barrio_keys) - 1: # 2 barrios por fila
            keyboard_barrios.append(temp_row)
            temp_row = []
    
    if not keyboard_barrios:
        logger.warning("ACCIDENT_HANDLER_V2: BARRIO_OPTIONS está vacío. Pidiendo ID numérico para ubicación.")
        await update.message.reply_text(
            "Tipo de accidente registrado.\n"
            "No hay opciones de barrio configuradas. Por favor, ingresa el ID numérico de la ubicación (si lo conoces, sino ingresa 0).",
            reply_markup=ReplyKeyboardRemove()
        )
        # Este es un fallback si BARRIO_OPTIONS está vacío, lo cual no debería pasar si está bien definido.
        # El estado sigue siendo REPORTING_BARRIO_SELECTION, pero el handler handle_barrio_selection
        # debería poder manejar un input numérico si no hay opciones.
        # Sin embargo, es mejor asegurar que BARRIO_OPTIONS esté poblado.
        # Por ahora, asumimos que el usuario escribirá un número si esto pasa.
        return REPORTING_BARRIO_SELECTION # Dejar que el siguiente handler intente parsear un número
    else:
         await update.message.reply_text(
            "Tipo de accidente registrado.\n"
            "Ahora, selecciona el barrio donde ocurrió el accidente:",
            reply_markup=ReplyKeyboardMarkup(keyboard_barrios, one_time_keyboard=True, resize_keyboard=True) # No usar input_field_placeholder con teclados de opciones
        )
    return REPORTING_BARRIO_SELECTION

async def handle_barrio_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección del barrio para determinar la ubicacion_id."""
    selected_barrio_text = update.message.text.strip()
    ubicacion_id_from_barrio = BARRIO_OPTIONS.get(selected_barrio_text)

    if ubicacion_id_from_barrio is None:
        # Si el usuario escribe algo que no es una opción, intentar parsearlo como ID numérico
        # Esto sirve de fallback si BARRIO_OPTIONS estuviera vacío y se pidió ID numérico.
        try:
            ubicacion_id_from_barrio = int(selected_barrio_text)
            logger.info(f"ACCIDENT_HANDLER_V2: Barrio no seleccionado de lista, se interpretó como ID numérico: {ubicacion_id_from_barrio}")
            # Aquí podrías querer validar si este ID numérico es válido contra tu tabla de ubicaciones.
        except ValueError:
            await update.message.reply_text("Opción de barrio no válida. Por favor, selecciona un barrio de la lista o ingresa un ID numérico de ubicación si se te indicó.")
            # Re-mostrar teclado de barrios
            barrio_keys = list(BARRIO_OPTIONS.keys())
            keyboard_barrios = []
            temp_row = []
            for i, barrio_key in enumerate(barrio_keys):
                temp_row.append(KeyboardButton(barrio_key))
                if len(temp_row) == 2 or i == len(barrio_keys) - 1:
                    keyboard_barrios.append(temp_row)
                    temp_row = []
            if keyboard_barrios: # Solo mostrar si hay opciones
                 await update.message.reply_text(
                    "Selecciona el barrio donde ocurrió el accidente:",
                    reply_markup=ReplyKeyboardMarkup(keyboard_barrios, one_time_keyboard=True, resize_keyboard=True)
                )
            return REPORTING_BARRIO_SELECTION
        
    context.user_data['current_accident_report_v2_data']['ubicacion_id'] = ubicacion_id_from_barrio
    context.user_data['current_accident_report_v2_data']['barrio_nombre_seleccionado'] = selected_barrio_text # Guardar nombre para resumen
    logger.info(f"ACCIDENT_HANDLER_V2: Ubicación ID (desde barrio): {ubicacion_id_from_barrio} (seleccionado/ingresado: '{selected_barrio_text}')")
    return await show_final_confirmation_v2(update, context)

async def show_final_confirmation_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Muestra el resumen de los datos recolectados y pide confirmación final."""
    report_data = context.user_data.get('current_accident_report_v2_data', {})
    
    fecha_display = "No especificada"
    if report_data.get('fecha'):
        try:
            dt_utc = datetime.datetime.fromisoformat(report_data['fecha'].replace("Z", "+00:00"))
            dt_colombia = dt_utc.astimezone(COLOMBIA_TZ)
            fecha_display = dt_colombia.strftime("%d/%m/%Y %I:%M %p")
        except: fecha_display = report_data.get('fecha')
    
    cond_vic_id = report_data.get('condicion_victima_id')
    cond_vic_display = next((k for k, v in CONDICION_VICTIMA_OPTIONS.items() if v == cond_vic_id), f"ID: {cond_vic_id}")
    
    grav_id = report_data.get('gravedad_victima_id')
    grav_display = next((k for k, v in GRAVEDAD_VICTIMA_OPTIONS.items() if v == grav_id), f"ID: {grav_id}")

    tipo_acc_id = report_data.get('tipo_accidente_id')
    tipo_acc_display = next((k for k, v in TIPO_ACCIDENTE_OPTIONS.items() if v == tipo_acc_id), f"ID: {tipo_acc_id}")
    
    barrio_nombre_display = report_data.get('barrio_nombre_seleccionado', 'N/A')
    ubicacion_id_display = report_data.get('ubicacion_id', 'N/A')

    summary_parts = [
        "📝 *Resumen del Reporte de Accidente*",
        "Verifica la información antes de enviar:\n",
        f"*Fecha y Hora (UTC)*: {report_data.get('fecha', 'N/A')} ({fecha_display} Colombia)",
        f"*Sexo Víctima*: {report_data.get('sexo_victima', 'N/A')}",
        f"*Edad Víctima*: {report_data.get('edad_victima', 'N/A')} años",
        f"*Cantidad Víctimas*: {report_data.get('cantidad_victima', 'N/A')}",
        f"*Condición Víctima*: {cond_vic_display}",
        f"*Gravedad Víctima*: {grav_display}",
        f"*Tipo Accidente*: {tipo_acc_display}",
        f"*Ubicación (Barrio Seleccionado/ID)*: {barrio_nombre_display if ubicacion_id_display !=0 else 'ID Numérico: '+ str(ubicacion_id_display)} (ID para Payload: {ubicacion_id_display})\n",
        "¿Enviar este reporte?"
    ]
    confirmation_keyboard = [["✅ Sí, enviar"], ["❌ No, cancelar"]]
    await update.message.reply_text(
        "\n".join(summary_parts),
        reply_markup=ReplyKeyboardMarkup(confirmation_keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return REPORTING_ACCIDENT_CONFIRMATION

async def accident_final_confirmation_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la confirmación final y envía el payload exacto a la API."""
    user_choice = update.message.text
    if "✅ Sí, enviar" not in user_choice:
        await update.message.reply_text("Reporte cancelado.", reply_markup=ReplyKeyboardRemove())
        context.user_data.pop('current_accident_report_v2_data', None)
        return ConversationHandler.END

    # Construir el payload EXACTAMENTE como se especificó
    report_data_from_user = context.user_data.get('current_accident_report_v2_data', {})
    api_payload = {
        "fecha": report_data_from_user.get('fecha', datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")),
        "sexo_victima": report_data_from_user.get('sexo_victima', "O"), # Default a 'O' si no se proveyó
        "edad_victima": int(report_data_from_user.get('edad_victima', 0)),
        "cantidad_victima": int(report_data_from_user.get('cantidad_victima', 1)),
        "condicion_victima_id": int(report_data_from_user.get('condicion_victima_id', 0)), # Default a 0 si no se proveyó
        "gravedad_victima_id": int(report_data_from_user.get('gravedad_victima_id', 0)),
        "tipo_accidente_id": int(report_data_from_user.get('tipo_accidente_id', 0)),
        "ubicacion_id": int(report_data_from_user.get('ubicacion_id', 0)) # Default a 0 si no se proveyó
        # El campo "usuario_id" se añadirá cuando se implemente el login.
    }
    
    # TODO: Añadir usuario_id del usuario logueado (Parte 2)
    # backend_user_id = context.user_data.get('backend_user_id')
    # if backend_user_id:
    #     api_payload['usuario_id'] = backend_user_id
    # else:
    #     logger.error("ACCIDENT_HANDLER_V2: Falta backend_user_id para el reporte. El usuario debería estar logueado.")
    #     await update.message.reply_text("Error: No se pudo identificar tu usuario. Por favor, intenta iniciar sesión de nuevo con /login.", reply_markup=ReplyKeyboardRemove())
    #     return ConversationHandler.END


    logger.info(f"ACCIDENT_HANDLER_V2: Enviando payload final a la API: {api_payload}")
    processing_msg = await update.message.reply_text("Procesando tu reporte...", reply_markup=ReplyKeyboardRemove())
    
    api_response = await report_accident_api(api_payload)

    if api_response and not api_response.get("error") and (api_response.get("id") or api_response.get("id_accidente")):
        accidente_id_creado = api_response.get("id", api_response.get("id_accidente", "N/A"))
        success_msg = (f"¡Reporte enviado con éxito! 👍\nID del Accidente Registrado: *{accidente_id_creado}*\n\nGracias por tu colaboración.")
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, text=success_msg, parse_mode='Markdown')
    else:
        error_detail = "No se pudo procesar el reporte en el servidor."
        if isinstance(api_response, dict):
            error_detail = api_response.get("detail", str(api_response.get("error_message", str(api_response)))) # Intentar obtener más detalles
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, text=f"Hubo un problema al enviar el reporte: _{error_detail}_")
        logger.error(f"ACCIDENT_HANDLER_V2: Error al enviar reporte a API: {api_response}")

    context.user_data.pop('current_accident_report_v2_data', None)
    return ConversationHandler.END

async def cancel_report_v2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el flujo de reporte v2."""
    await update.message.reply_text("Reporte de accidente cancelado.", reply_markup=ReplyKeyboardRemove())
    context.user_data.pop('current_accident_report_v2_data', None)
    return ConversationHandler.END

# Nuevo ConversationHandler para el flujo de reporte v2 con opciones
report_accident_v2_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("reportar", start_accident_report_v2)],
    states={
        REPORTING_ACCIDENT_DATETIME_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_accident_datetime_choice)],
        REPORTING_VICTIM_SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_victim_sex)],
        REPORTING_VICTIM_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_victim_age)],
        REPORTING_VICTIM_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_victim_count)],
        REPORTING_VICTIM_CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_victim_condition)],
        REPORTING_ACCIDENT_GRAVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_accident_gravity)],
        REPORTING_ACCIDENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_accident_type)],
        REPORTING_BARRIO_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_barrio_selection)], # Nuevo handler para barrio
        REPORTING_ACCIDENT_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, accident_final_confirmation_v2)],
    },
    fallbacks=[CommandHandler("cancelar", cancel_report_v2)],
)


# --- FUNCIONES EXISTENTES PARA CONSULTA DE DETALLES (sin cambios, ya deberían estar en tu archivo) ---
# (Asegúrate de que estas funciones (_format_accidente_details, detalle_accidente_command, 
#  handle_natural_language_accident_query) estén presentes y sean las últimas versiones que te di)
def _format_accidente_details(accidente_data: Optional[Dict[str, Any]]) -> str:
    if not accidente_data: return "No se pudo obtener la información del accidente o no se encontraron datos."
    id_accidente = accidente_data.get('id', 'N/A')
    fecha_hora_display = "No especificada"
    fecha_hora_iso = accidente_data.get('fecha') 
    if fecha_hora_iso:
        try:
            dt_obj = datetime.datetime.fromisoformat(str(fecha_hora_iso).replace("Z", "+00:00"))
            dt_utc = dt_obj.astimezone(datetime.timezone.utc) if dt_obj.tzinfo else dt_obj.replace(tzinfo=datetime.timezone.utc)
            dt_colombia = dt_utc.astimezone(COLOMBIA_TZ)
            fecha_hora_display = dt_colombia.strftime("%d de %B de %Y a las %I:%M %p (%Z)")
        except Exception as e: logger.error(f"Error al formatear fecha '{fecha_hora_iso}': {e}"); fecha_hora_display = str(fecha_hora_iso)
    ubicacion_obj = accidente_data.get('ubicacion', {})
    ubicacion_display_parts = []
    if via1 := ubicacion_obj.get('primer_via', {}): ubicacion_display_parts.append(f"{via1.get('tipo_via', {}).get('nombre', '')} {via1.get('numero_via', '')}".strip())
    if via2 := ubicacion_obj.get('segunda_via', {}): ubicacion_display_parts.append(f"{via2.get('tipo_via', {}).get('nombre', '')} {via2.get('numero_via', '')}".strip())
    ubicacion_vias = " con ".join(filter(None, ubicacion_display_parts))
    barrio_nombre = ubicacion_obj.get('barrio', {}).get('nombre', '')
    ubicacion_display = f"{ubicacion_vias}, Barrio {barrio_nombre}".strip(", ") if ubicacion_vias or barrio_nombre else "No especificada"
    if complemento := ubicacion_obj.get('complemento'): ubicacion_display += f" ({complemento})"
    if (lat := ubicacion_obj.get('latitud')) and (lon := ubicacion_obj.get('longitud')): ubicacion_display += f" (Lat: {lat:.5f}, Lon: {lon:.5f})"
    gravedad_display = accidente_data.get('gravedad', {}).get('nivel_gravedad', 'No especificada')
    tipo_accidente_display = accidente_data.get('tipo_accidente', {}).get('nombre', 'No especificado')
    details = [
        f"📄 *Detalles del Accidente (ID: {id_accidente})*", "-------------------------------------",
        f"🗓️ *Fecha y Hora*: {fecha_hora_display}", f"💥 *Tipo de Accidente*: {tipo_accidente_display}",
        f"📍 *Ubicación*: {ubicacion_display}", f"📊 *Gravedad Víctima*: {gravedad_display}",
        f"👤 *Condición Víctima*: {accidente_data.get('condicion_victima', {}).get('rol_victima', 'No especificada')}",
        f"🚻 *Sexo Víctima*: {accidente_data.get('sexo_victima', 'N/A')}",
        f"🎂 *Edad Víctima*: {accidente_data.get('edad_victima', 'N/A')}",
        f"🔢 *Cantidad de Víctimas*: {accidente_data.get('cantidad_victima', 'N/A')}",
    ]
    return "\n".join(details)

async def detalle_accidente_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id; logger.info(f"ACCIDENT_HANDLER: Usuario {user_id} ejecutó /detalle_accidente con args: {context.args}")
    if not context.args: await update.message.reply_text("Por favor, proporciona el ID del accidente. Ejemplo: `/detalle_accidente TU_ID`", parse_mode='Markdown'); return
    accidente_id_input = context.args[0] 
    await update.message.reply_text(f"Buscando información para el accidente ID: `{accidente_id_input}`...", parse_mode='Markdown')
    accidente_info = await get_accidente_by_id(accidente_id_input) 
    response_message = _format_accidente_details(accidente_info) if accidente_info else f"No se encontró información para el accidente ID: `{accidente_id_input}`."
    await update.message.reply_text(response_message, parse_mode='Markdown')

async def handle_natural_language_accident_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text: return
    message_text = update.message.text; user_id = update.effective_user.id
    logger.info(f"ACCIDENT_HANDLER (Natural Language): Usuario {user_id} envió mensaje: '{message_text}'")
    keyword_phrases = (r"dame\s+(los\s+)?detalles\s+(de\s+(la\s+|el\s+)?ID|del\s+accidente)|informaci[oó]n\s+del\s+(ID|accidente)|info\s+del\s+(ID|accidente)|qu[eé]\s+sabes\s+del\s+accidente|reporte\s+del\s+accidente|ver\s+accidente|accidente|ID|identificador")
    id_capture = r"([a-f0-9]{24}|\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b|\b\d{1,8}\b)" 
    pattern_with_keywords = rf"(?:{keyword_phrases})\s*{id_capture}"
    direct_id_patterns_list = [rf"\b{id_capture}\b"] 
    accidente_id_extracted = None
    match_keywords = re.search(pattern_with_keywords, message_text, re.IGNORECASE)
    if match_keywords: accidente_id_extracted = match_keywords.group(match_keywords.lastindex) 
    else:
        for direct_pattern in direct_id_patterns_list:
            match_direct = re.search(direct_pattern, message_text, re.IGNORECASE)
            if match_direct: accidente_id_extracted = match_direct.group(1); break 
    if accidente_id_extracted:
        accidente_id_extracted = accidente_id_extracted.strip()
        logger.info(f"ACCIDENT_HANDLER (Natural Language): ID '{accidente_id_extracted}' extraído de: '{message_text}'")
        await update.message.reply_text(f"Detecté que preguntas por el ID: `{accidente_id_extracted}`. Buscando...", parse_mode='Markdown')
        accidente_info = await get_accidente_by_id(accidente_id_extracted)
        response_message = _format_accidente_details(accidente_info) if accidente_info else f"No encontré info para ID: `{accidente_id_extracted}`."
        await update.message.reply_text(response_message, parse_mode='Markdown')
    else: logger.info(f"ACCIDENT_HANDLER (Natural Language): No se detectó ID en: '{message_text}'. Pasa a otros handlers.")


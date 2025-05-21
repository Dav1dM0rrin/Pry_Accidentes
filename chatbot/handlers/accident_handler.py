# chatbot/handlers/accident_handler.py
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram.constants import ParseMode
import logging
import html 
from ..api_client import APIClient
from .conversation_states import DESCRIPTION, LATITUDE, LONGITUDE, GRAVITY, CONFIRMATION

logger = logging.getLogger(__name__)
api_client = APIClient()

def _get_nested_value(data_dict, path, default='N/D'):
    """
    Obtiene un valor de un diccionario anidado usando una ruta de claves.
    Ejemplo: path=['ubicacion', 'latitud']
    """
    current = data_dict
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def _to_str_for_escape(value, default_str='N/D'):
    """Convierte un valor a string de forma segura para html.escape."""
    if isinstance(value, dict):
        # Si es un dict, y esperamos un valor textual, intentamos con claves comunes.
        # Para 'gravedad_victima', el texto está en 'nivel_gravedad'.
        # Para 'tipo_accidente', el texto está en 'nombre'.
        # Para 'condicion_victima', el texto está en 'rol_victima'.
        # Para 'ubicacion', el texto relevante podría ser 'complemento' o 'barrio.nombre'.
        # Esta función se vuelve más específica según el campo.
        return str(value.get('nivel_gravedad', value.get('nombre', value.get('rol_victima', str(value)))))
    elif value is None:
        return default_str
    elif not isinstance(value, str):
        return str(value)
    return value

async def report_accident_start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) inició el reporte de accidente con /reportar_accidente.")
    await update.message.reply_text(
        "¡Entendido! Vamos a reportar un accidente.\n"
        "Por favor, describe brevemente qué ocurrió (ej: Choque entre moto y carro, peatón atropellado)."
    )
    return DESCRIPTION

async def get_description(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    # Para el reporte, la descripción es el texto que el usuario ingresa.
    # Este será el campo 'descripcion' que se envía a la API.
    # Tu API backend deberá decidir si este texto va al campo 'complemento' de la tabla 'ubicacion'
    # o si tienes un campo de descripción general en tu modelo de Accidente en el backend.
    context.user_data['descripcion_reportada'] = user_input 
    logger.info(f"Descripción reportada por {update.effective_user.id}: {user_input}")
    await update.message.reply_text(
        "Gracias. Ahora, por favor, envía la latitud del lugar del accidente.\n"
        "Puedes obtenerla de Google Maps. Ejemplo: <code>10.987</code>",
        parse_mode=ParseMode.HTML
    )
    return LATITUDE

async def get_latitude(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        latitude = float(user_input)
        context.user_data['latitude'] = latitude
        logger.info(f"Latitud recibida de {update.effective_user.id}: {latitude}")
        await update.message.reply_text(
            "Latitud guardada. Ahora, por favor, envía la longitud.\n"
            "Ejemplo: <code>-74.789</code>",
            parse_mode=ParseMode.HTML
        )
        return LONGITUDE
    except ValueError:
        logger.warning(f"Entrada de latitud inválida de {update.effective_user.id}: {user_input}")
        await update.message.reply_text(
            "Latitud no válida. Inténtalo de nuevo. Ejemplo: <code>10.987</code>",
            parse_mode=ParseMode.HTML
        )
        return LATITUDE

async def get_longitude(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        longitude = float(user_input)
        context.user_data['longitude'] = longitude
        logger.info(f"Longitud recibida de {update.effective_user.id}: {longitude}")
        # En tu BD, 'gravedad_victima_id' es un FK. El usuario seleccionará el texto.
        # El backend deberá mapear "Leve", "Moderado", "Grave" al ID correspondiente.
        reply_keyboard = [['Leve', 'Moderado', 'Grave']] 
        await update.message.reply_text(
            "Longitud guardada. Selecciona la gravedad del accidente para la víctima principal:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return GRAVITY
    except ValueError:
        logger.warning(f"Entrada de longitud inválida de {update.effective_user.id}: {user_input}")
        await update.message.reply_text(
            "Longitud no válida. Inténtalo de nuevo. Ejemplo: <code>-74.789</code>",
            parse_mode=ParseMode.HTML
        )
        return LONGITUDE

async def get_gravity(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text # Será "Leve", "Moderado", o "Grave"
    if user_input not in ['Leve', 'Moderado', 'Grave']:
        logger.warning(f"Entrada de gravedad inválida de {update.effective_user.id}: {user_input}")
        await update.message.reply_text("Selecciona una opción válida para la gravedad.")
        return GRAVITY
        
    context.user_data['gravedad_reportada'] = user_input
    logger.info(f"Gravedad reportada por {update.effective_user.id}: {user_input}")
    
    desc_escaped = html.escape(context.user_data['descripcion_reportada'])
    gravity_escaped = html.escape(context.user_data['gravedad_reportada'])
    
    summary = (
        "<b>Resumen del Reporte:</b>\n"
        f"Descripción: {desc_escaped}\n"
        f"Latitud: {context.user_data['latitude']}\n"
        f"Longitud: {context.user_data['longitude']}\n"
        f"Gravedad: {gravity_escaped}\n\n"
        "¿Es correcta esta información? (Sí/No)"
    )
    reply_keyboard = [['Sí', 'No']]
    await update.message.reply_text(
        summary,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CONFIRMATION

async def confirm_report(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.lower()
    user = update.effective_user
    if user_input == 'sí' or user_input == 'si':
        logger.info(f"Usuario {user.id} confirmó el reporte.")
        await update.message.reply_text("Confirmado. Enviando reporte...", reply_markup=ReplyKeyboardRemove())
        
        # El `api_client.report_accident` espera: descripcion, latitud, longitud, gravedad (string), usuario_id
        # Tu backend deberá mapear la gravedad "Leve", "Moderado", "Grave" al ID correspondiente de `accidente_gravedadvictima`
        # y la `descripcion` al campo `complemento` de `accidente_ubicacion` o a un campo de descripción general.
        report_data = {
            "descripcion": context.user_data['descripcion_reportada'], 
            "latitud": context.user_data['latitude'],
            "longitud": context.user_data['longitude'],
            "gravedad": context.user_data['gravedad_reportada'], # Enviar el string, backend lo mapea a ID
            "usuario_id": user.id 
        }
        
        response = api_client.report_accident(**report_data)

        if response and not (isinstance(response, dict) and response.get("error")):
            # Asumimos que la respuesta de éxito de la API para POST contiene el ID del nuevo accidente
            # y otros campos que tu API decida devolver.
            # Si la API devuelve el objeto completo del accidente creado, podrías mostrar más detalles.
            # Por ahora, solo el ID.
            api_response_id = "N/A"
            if isinstance(response, dict): # Si la API devuelve un dict
                api_response_id = response.get('id', 'N/A')
            
            await update.message.reply_text(f"¡Accidente reportado exitosamente! ID del reporte: {api_response_id}\n"
                                            "Gracias por tu colaboración.")
            logger.info(f"Accidente reportado exitosamente por {user.id}. Respuesta API: {response}")
        else:
            error_detail = "Respuesta inesperada de la API."
            if isinstance(response, dict) and response.get("error"):
                 error_detail = response.get("detail", "No se pudo obtener detalle del error.")
            elif response is None:
                 error_detail = "La API no devolvió una respuesta válida (JSON)."
            await update.message.reply_text(f"Hubo un error al reportar el accidente: {error_detail}\n"
                                            "Por favor, inténtalo de nuevo más tarde.")
            logger.error(f"Error al reportar accidente para {user.id}. Detalles: {response}")
            
        context.user_data.clear()
        return ConversationHandler.END
    elif user_input == 'no':
        logger.info(f"Usuario {user.id} canceló el reporte en la confirmación.")
        await update.message.reply_text("Reporte cancelado.", reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Por favor, responde 'Sí' o 'No'.")
        return CONFIRMATION

async def cancel_report(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) canceló con /cancelar.")
    await update.message.reply_text("Proceso de reporte cancelado.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

async def view_accidents(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) solicitó /ver_accidentes con args: {context.args}")
    await update.message.reply_chat_action('typing')
    
    default_limit = 3
    display_limit = default_limit
    max_limit = 10 

    if context.args:
        try:
            requested_limit = int(context.args[0])
            if 0 < requested_limit <= max_limit: display_limit = requested_limit
            elif requested_limit > max_limit:
                await update.message.reply_text(f"Solo puedo mostrar hasta {max_limit} accidentes. Mostrando {max_limit}.")
                display_limit = max_limit
            else: await update.message.reply_text(f"Número inválido. Mostrando los {default_limit} más recientes.")
        except ValueError: await update.message.reply_text(f"No entendí el número. Mostrando los {default_limit} más recientes.")
        except IndexError: pass
    
    accidents_response = api_client.get_accidents(limit=display_limit)

    if accidents_response is None:
        logger.error("Error al obtener accidentes: Respuesta API no JSON o vacía.")
        await update.message.reply_text("No pude obtener la lista de accidentes: Respuesta inválida de la API.")
    elif isinstance(accidents_response, dict) and accidents_response.get("error"):
        error_detail = accidents_response.get("detail", "Error desconocido")
        logger.error(f"Error al obtener accidentes: {error_detail}")
        await update.message.reply_text(f"No pude obtener la lista de accidentes: {error_detail}")
    elif isinstance(accidents_response, list):
        accidents = accidents_response
        if accidents:
            message_parts = [f"<b>Mostrando los últimos {len(accidents)} accidentes reportados (de {display_limit} solicitados):</b>\n"]
            for acc_data in accidents: # acc_data es un diccionario por cada accidente
                # Asumimos que tu API ahora devuelve los nombres y no solo los IDs
                # Si devuelve objetos anidados, ajusta los .get() con _get_nested_value
                
                # Para la descripción, usamos 'complemento' de 'ubicacion' si existe, sino "N/D"
                # Si tu API devuelve 'descripcion' directamente en el objeto acc_data, úsalo.
                descripcion_val = _get_nested_value(acc_data, ['ubicacion', 'complemento'], 'Sin descripción')
                if descripcion_val == 'Sin descripción' and 'descripcion' in acc_data : # Fallback si hay un campo 'descripcion' directo
                    descripcion_val = acc_data.get('descripcion', 'Sin descripción')
                desc_escaped = html.escape(_to_str_for_escape(descripcion_val, 'Sin descripción')[:100])
                
                fecha_val = acc_data.get('fecha', 'Fecha desconocida') # De la tabla accidente_accidente
                fecha_escaped = html.escape(_to_str_for_escape(fecha_val))
                
                # Para gravedad, esperamos que la API devuelva el texto (ej. "Herido")
                # Si devuelve el objeto anidado: gravedad_val = _get_nested_value(acc_data, ['gravedad_victima', 'nivel_gravedad'], 'N/D')
                gravedad_val = acc_data.get('gravedad', _get_nested_value(acc_data, ['gravedad_victima', 'nivel_gravedad'], 'N/D'))
                gravedad_escaped = html.escape(_to_str_for_escape(gravedad_val))
                
                lat = _get_nested_value(acc_data, ['ubicacion', 'latitud'], 0)
                lon = _get_nested_value(acc_data, ['ubicacion', 'longitud'], 0)

                message_parts.append(
                    f"🆔 <b>ID:</b> {acc_data.get('id', 'N/A')}\n"
                    f"📝 Desc: {desc_escaped}...\n"
                    f"📅 Fecha: {fecha_escaped}\n"
                    f"🚦 Gravedad: {gravedad_escaped}\n"
                    f"<a href='https://www.google.com/maps?q={lat},{lon}'>Ver en Mapa</a>\n" # Enlace de Google Maps estándar
                    f"Detalles: /detalle_accidente {acc_data.get('id', '')}\n"
                    "--------------------"
                )
            final_message = "\n".join(message_parts)
            if len(final_message) > 4096:
                await update.message.reply_text(f"Se encontraron {len(accidents)} accidentes, pero el mensaje es demasiado largo. Intenta solicitar menos o verlos de uno en uno.")
                logger.warning("El mensaje de /ver_accidentes excedió el límite de Telegram.")
            else:
                await update.message.reply_text(final_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"No se encontraron accidentes para los {display_limit} más recientes solicitados.")
    else:
        logger.error(f"Respuesta API inesperada para get_accidents: {accidents_response}")
        await update.message.reply_text("No pude obtener la lista de accidentes (formato de respuesta inesperado).")

async def accident_detail(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Proporciona el ID. Ej: /detalle_accidente <code>123</code>", parse_mode=ParseMode.HTML)
        return
    try:
        accident_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("El ID debe ser un número. Ej: /detalle_accidente <code>123</code>", parse_mode=ParseMode.HTML)
        return

    logger.info(f"Usuario {user.id} solicitó detalle ID: {accident_id}.")
    await update.message.reply_chat_action('typing')
    response = api_client.get_accident_detail(accident_id)

    if response is None:
        logger.error(f"Error al obtener detalle {accident_id}: Respuesta API no JSON o vacía.")
        await update.message.reply_text(f"No pude obtener detalles del accidente {accident_id}: Respuesta inválida de la API.")
    elif isinstance(response, dict) and response.get("error"):
        error_detail = response.get("detail", "Error desconocido")
        status_code = response.get("status_code")
        if status_code == 404:
            await update.message.reply_text(f"No se encontró accidente con ID {accident_id}.")
        else:
            await update.message.reply_text(f"No pude obtener detalles: {error_detail}")
    elif isinstance(response, dict): # Asumimos que un dict sin "error" es el detalle del accidente
        acc_data = response
        
        # Mapeo de campos desde la estructura de tu BD (o como la API los devuelva)
        # Descripción: Usaremos ubicacion.complemento o un campo 'descripcion' si existe.
        descripcion_val = _get_nested_value(acc_data, ['ubicacion', 'complemento'], 'Sin descripción')
        if descripcion_val == 'Sin descripción' and 'descripcion' in acc_data:
             descripcion_val = acc_data.get('descripcion', 'Sin descripción')
        desc_escaped = html.escape(_to_str_for_escape(descripcion_val, 'Sin descripción'))
        
        fecha_val = acc_data.get('fecha', 'N/D') # Directo de accidente_accidente
        fecha_escaped = html.escape(_to_str_for_escape(fecha_val))
        
        # Gravedad: Esperamos que la API devuelva el texto, ej., a través de un join.
        # Si devuelve el objeto anidado: gravedad_val = _get_nested_value(acc_data, ['gravedad_victima', 'nivel_gravedad'], 'N/D')
        # Si tu API devuelve 'gravedad' directamente como string:
        gravedad_val = acc_data.get('gravedad', _get_nested_value(acc_data, ['gravedad_victima', 'nivel_gravedad'], 'N/D'))
        gravedad_escaped = html.escape(_to_str_for_escape(gravedad_val))
        
        lat = _get_nested_value(acc_data, ['ubicacion', 'latitud'], 'N/D')
        lon = _get_nested_value(acc_data, ['ubicacion', 'longitud'], 'N/D')
        
        # Otros campos de tu tabla accidente_accidente
        sexo_victima_val = acc_data.get('sexo_victima', 'N/D')
        edad_victima_val = acc_data.get('edad_victima', 'N/D')
        cantidad_victima_val = acc_data.get('cantidad_victima', 'N/D')
        
        # Campos de tablas relacionadas (esperando que la API haga el JOIN y devuelva los nombres)
        tipo_accidente_val = acc_data.get('tipo_accidente', _get_nested_value(acc_data, ['tipo_accidente', 'nombre'], 'N/D'))
        condicion_victima_val = acc_data.get('condicion_victima', _get_nested_value(acc_data, ['condicion_victima', 'rol_victima'], 'N/D'))
        barrio_val = _get_nested_value(acc_data, ['ubicacion', 'barrio', 'nombre_barrio'], 'N/D') # Asumiendo que barrio tiene 'nombre_barrio'
        
        # Escapar todos los valores textuales
        sexo_victima_escaped = html.escape(_to_str_for_escape(sexo_victima_val))
        tipo_accidente_escaped = html.escape(_to_str_for_escape(tipo_accidente_val))
        condicion_victima_escaped = html.escape(_to_str_for_escape(condicion_victima_val))
        barrio_escaped = html.escape(_to_str_for_escape(barrio_val))
        
        # Usuario ID (ya es un número o string, escapar por si acaso)
        usuario_id_val = acc_data.get('usuario_id', 'N/D')
        usuario_id_escaped = html.escape(_to_str_for_escape(usuario_id_val))

        message = (
            f"<b>Detalles del Accidente ID: {acc_data.get('id', 'N/A')}</b>\n"
            f"📝 <b>Descripción/Complemento:</b> {desc_escaped}\n"
            f"📅 <b>Fecha:</b> {fecha_escaped}\n"
            f"🌍 <b>Ubicación:</b> Lat: {lat}, Lon: {lon}\n"
            f"🏘️ <b>Barrio:</b> {barrio_escaped}\n"
            f"🚦 <b>Gravedad Víctima:</b> {gravedad_escaped}\n"
            f"💥 <b>Tipo Accidente:</b> {tipo_accidente_escaped}\n"
            f"👤 <b>Condición Víctima:</b> {condicion_victima_escaped}\n"
            f"🚻 <b>Sexo Víctima:</b> {sexo_victima_escaped}\n"
            f"🎂 <b>Edad Víctima:</b> {edad_victima_val}\n" # Número, no necesita escape
            f"👥 <b>Cantidad Víctimas:</b> {cantidad_victima_val}\n" # Número, no necesita escape
            f"🆔 <b>Reportado por Usuario ID:</b> {usuario_id_escaped}\n"
            f"<a href='https://www.google.com/maps?q={lat},{lon}'>📍 Ver en Google Maps</a>"
        )
        await update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        logger.error(f"Respuesta API inesperada para get_accident_detail ({accident_id}): {response}")
        await update.message.reply_text(f"No pude obtener detalles del accidente {accident_id} (formato inesperado).")


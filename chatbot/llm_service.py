# chatbot/llm_service.py

import requests
import logging
import json # Necesario para parsear la respuesta JSON del LLM

# Importa la configuración del LLM
# Asegúrate de que esta importación relativa sea correcta dependiendo de dónde esté la carpeta 'chatbot'
# Si 'chatbot' es la carpeta raíz de tu proyecto, '.config' está bien.
try:
    from .config import LLM_API_KEY, LLM_API_URL, LLM_MODEL_NAME
except ImportError:
    # Manejar el caso si el archivo config no existe o no se puede importar,
    # por ejemplo, si este archivo se ejecuta directamente o la estructura de importación cambia.
    # si se ejecuta desde el punto de entrada principal.
    logging.error("No se pudo importar la configuración del LLM desde .config. Asegúrate de que 'config.py' existe y está en la ruta de importación correcta.")
    LLM_API_KEY = None
    LLM_API_URL = None
    LLM_MODEL_NAME = None


logger = logging.getLogger(__name__)

# Mensaje del sistema para guiar al LLM
SYSTEM_MESSAGE = """
Eres un asistente chatbot experto en datos de accidentes de Barranquilla. Tu tarea es comprender la solicitud del usuario e identificar su intención y cualquier parámetro relevante.

Tu respuesta debe ser SIEMPRE un objeto JSON válido. NO incluyas texto explicativo adicional ni formateo que no sea parte del JSON.

El JSON debe tener las siguientes claves:
- "intent": Una cadena que identifique la intención principal. Las intenciones posibles son:
    - "list_recent_accidents": El usuario quiere ver los accidentes más recientes.
    - "find_accident_by_id": El usuario quiere buscar un accidente específico por su número de ID.
    - "greet": El usuario está saludando o mostrando gratitud.
    - "unknown": La intención del usuario no es clara o no se relaciona con los accidentes.
- "parameters": Un objeto JSON (diccionario) que contenga los parámetros extraídos para la intención.
    - Para "list_recent_accidents": {} (vacío)
    - Para "find_accident_by_id": {"accident_id": <el ID numérico del accidente mencionado por el usuario>}
    - Para "greet": {} (vacío)
    - Para "unknown": {"user_message": "<el mensaje original del usuario>"}

Ejemplo de respuesta esperada para "Quiero ver los ultimos 10 accidentes":
{
  "intent": "list_recent_accidents",
  "parameters": {}
}
"""


def get_intent_and_parameters(user_message: str) -> dict:
    """
    Envía el mensaje del usuario al LLM para obtener la intención y los parámetros.
    Retorna el diccionario JSON parseado del LLM o un diccionario indicando error/indisponibilidad.
    """
    # Verifica si la configuración del LLM está completa. Si no, no intentamos la llamada API.
    if not LLM_API_KEY or not LLM_API_URL or not LLM_MODEL_NAME:
        logger.error("Configuración del LLM incompleta (LLM_API_KEY, LLM_API_URL, o LLM_MODEL_NAME faltan). No se puede usar el servicio LLM.")
        # Retorna un diccionario con una intención especial 'llm_unavailable'
        # Usamos 'error' como intent general para problemas del servicio LLM
        return {"intent": "error", "parameters": {"message": "Servicio LLM no configurado correctamente."}}

    # Prepara las cabeceras de la petición a la API del LLM
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}", # Autenticación con la API Key
        "Content-Type": "application/json"       # Indicamos que enviamos JSON
    }

    # Prepara el cuerpo de la petición. El formato exacto puede variar ligeramente
    # entre proveedores de LLM, pero este formato 'messages' es muy común (OpenAI, etc.).
    data = {
        "model": LLM_MODEL_NAME, # Especifica el modelo a usar
        "messages": [ # Lista de mensajes que forman la conversación para el LLM
            {"role": "system", "content": SYSTEM_MESSAGE}, # Mensaje del sistema para guiar
            {"role": "user", "content": user_message}      # Mensaje del usuario actual
        ],
        "temperature": 0.0, # La temperatura controla la aleatoriedad (0.0 es más determinista, ideal para extracción)
        # Si tu LLM soporta forzar la salida JSON, ¡úsa este parámetro!
        # Por ejemplo, para OpenAI Chat Completions API (>=gpt-4-1106):
     
    }

    logger.info(f"Enviando mensaje a LLM para análisis: '{user_message}'")

    try:
        # Realiza la petición POST a la API del LLM
        # Añade un timeout para evitar que la petición se quede colgada
        # Un timeout razonable depende de la latencia esperada del LLM. 20 segundos puede ser suficiente.
        response = requests.post(LLM_API_URL, headers=headers, json=data, timeout=20)
        response.raise_for_status() # Lanza una excepción HTTPError para respuestas de error (4xx o 5xx)

        llm_response = response.json() # Convierte la respuesta JSON de la API a un diccionario/lista Python

        content = llm_response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()


        logger.debug(f"Respuesta cruda del LLM (content): {content}") # Usamos debug para no saturar logs con contenido largo

        # Intenta extraer y parsear el JSON del contenido recibido del LLM
        # Intentamos limpiar eso antes de parsear para ser más tolerantes.
        clean_content = content
        if content.startswith('```json'):
            clean_content = content[len('```json'):] # Elimina '```json'
            if clean_content.endswith('```'):
                clean_content = clean_content[:-len('```')] # Elimina '```'
        clean_content = clean_content.strip() # Elimina espacios en blanco extra alrededor

        logger.debug(f"Contenido limpiado para parseo JSON: '{clean_content}'")

        # Asegurarse de que el contenido no esté vacío después de limpiar
        if not clean_content:
             logger.warning("El contenido de respuesta del LLM está vacío o solo contenía el bloque de código markdown sin JSON válido.")
             # Si el LLM respondió con contenido vacío después de limpiar, lo tratamos como desconocido/inválido.
             # Añadimos detalles para depuración.
             return {"intent": "unknown", "parameters": {"user_message": user_message, "llm_parse_error": "Respuesta vacía o ilegible del LLM después de limpiar.", "llm_raw_content": content}}

        # Intentar parsear el contenido limpiado como JSON
        # Si el LLM siguió las instrucciones, esto debería ser un JSON válido.
        try:
            intent_data = json.loads(clean_content)
        except json.JSONDecodeError as e:
             # Captura errores específicos de JSON Decode aquí, antes del catch general.
             logger.error(f"Error al parsear el contenido limpiado del LLM como JSON: {e}. Contenido que intentó parsear: '{clean_content}'. Respuesta cruda: '{content}'")
             # Retorna unknown si la respuesta del LLM no era un JSON válido.
             return {"intent": "unknown", "parameters": {"user_message": user_message, "llm_parse_error": f"La respuesta del LLM no es JSON válido: {e}", "llm_raw_content": content}}


        # Validar la estructura básica del JSON que esperamos que el LLM devuelva
        # Debe tener las claves "intent" y "parameters"
        if isinstance(intent_data, dict) and "intent" in intent_data and "parameters" in intent_data and isinstance(intent_data["parameters"], dict):
            # Aquí podrías añadir validaciones más específicas si necesitas,
            # por ejemplo, verificar el tipo de dato de "accident_id" si "intent" es "find_accident_by_id".
            # Por ahora, solo validamos la estructura básica.
            logger.info(f"LLM parseado exitosamente: Intent='{intent_data.get('intent')}', Params={intent_data.get('parameters')}")
            return intent_data # Retorna el diccionario JSON parseado si es válido y tiene la estructura esperada
        else:
            # Si el JSON es válido pero no tiene la estructura de claves/tipos esperada, tratamos como desconocido.
            logger.warning(f"La respuesta del LLM tiene formato JSON pero no la estructura esperada ('intent' y 'parameters' como dicts). Contenido: '{clean_content}'. Respuesta completa de la API: {llm_response}")
            return {"intent": "unknown", "parameters": {"user_message": user_message, "llm_parse_error": "Formato JSON incorrecto o faltan/tipos incorrectos de claves ('intent', 'parameters')", "llm_raw_content": content, "llm_parsed_structure": intent_data}}

    except requests.exceptions.Timeout:
        logger.error(f"Tiempo de espera agotado ({20}s) al llamar a la API del LLM {LLM_API_URL}.")
        # Retorna un diccionario indicando un error de timeout de la API del LLM
        return {"intent": "error", "parameters": {"message": "El LLM tardó demasiado en responder. Intenta de nuevo más tarde."}}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al llamar a la API del LLM {LLM_API_URL}: {e}")
        # Retorna un diccionario indicando un error general de comunicación con el LLM
        return {"intent": "error", "parameters": {"message": f"Error de comunicación con el servicio LLM: {e}"}}
    except Exception as e:
        # Captura cualquier otro error inesperado durante el proceso (fuera de las excepciones de requests y json).
        logger.critical(f"Ocurrió un error inesperado en llm_service.get_intent_and_parameters: {e}", exc_info=True) # exc_info=True para loguear el traceback
        return {"intent": "error", "parameters": {"message": f"Ocurrió un error interno al procesar la solicitud del LLM: {e}"}}


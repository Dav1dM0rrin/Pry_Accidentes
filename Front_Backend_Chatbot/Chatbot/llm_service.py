# Archivo: chatbot/llm_service.py
# Este servicio encapsula la lógica para interactuar con el modelo de lenguaje Gemini.

import google.generativeai as genai
from chatbot.config import GEMINI_API_KEY # Importa la clave API desde la configuración.
from chatbot.bot_logging import logger # Usa el logger configurado para la aplicación.
import json # Necesario para parsear respuestas JSON del LLM y formatear datos.

# --- Constantes y Configuración del Modelo ---
MODEL_NAME = 'gemini-1.5-flash-latest' # Modelo de Gemini a utilizar.
USER_ROLE = "user" # Rol del usuario en el historial de chat.
MODEL_ROLE = "model" # Rol del modelo (Gemini) en el historial de chat.

# Configuración global del SDK de Gemini.
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Opciones de generación (puedes ajustarlas según necesites).
    # Por ejemplo, `temperature` controla la creatividad, `top_p` y `top_k` el muestreo de tokens.
    generation_config = genai.types.GenerationConfig(
        # temperature=0.7, # Ejemplo: un valor más bajo para respuestas más deterministas.
        # max_output_tokens=1024, # Ejemplo: limitar la longitud de la respuesta.
    )
    # Podrías añadir safety_settings si necesitas ajustar los filtros de contenido.
    # safety_settings = [ ... ]

    # Inicializa el modelo generativo.
    llm_model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
        # system_instruction se puede usar aquí si el modelo lo soporta directamente para prompts de sistema.
        # system_instruction="Eres 'Asistente Vial Barranquilla'...",
    )
    logger.info(f"Modelo Gemini ({MODEL_NAME}) configurado exitosamente.")
except Exception as e:
    logger.critical(f"CRÍTICO: Error al configurar el SDK de Gemini: {e}. El servicio LLM no funcionará.", exc_info=True)
    llm_model = None # Asegura que el modelo es None si falla la configuración.


# Almacén en memoria para los historiales de chat.
# Clave: user_id (string), Valor: objeto `ChatSession` del SDK de Gemini.
# Para producción, considera una solución persistente (Redis, base de datos) si necesitas que los historiales sobrevivan reinicios.
conversation_sessions_store = {}

# --- Prompt de Sistema Detallado ---
# Este prompt define el comportamiento, rol y capacidades del LLM. Es fundamental ajustarlo bien.
SYSTEM_PROMPT_TEXT = """
Eres 'Asistente Vial Barranquilla', un chatbot IA avanzado, amigable, empático y muy servicial, especializado en temas de movilidad y accidentes de tránsito para la ciudad de Barranquilla, Colombia. Tu objetivo es asistir a los ciudadanos de manera eficiente y clara.

Tus Propósitos Principales son:
1.  **Reportar Accidentes**: Ayudar a los usuarios a reportar accidentes de tránsito. Debes guiar al usuario pacientemente para obtener:
    * Descripción detallada de lo sucedido.
    * Ubicación precisa (dirección completa, barrio, puntos de referencia notables, o pedir que compartan su ubicación de Telegram).
    * Fecha y hora exactas del evento (si no fue "ahora mismo").
    * Gravedad estimada del accidente (Leve, Moderada, Grave).
    Indica al usuario que puede usar el comando /reportar para un flujo guiado paso a paso.
2.  **Consultar Información de Accidentes**: Proveer información sobre accidentes ocurridos en Barranquilla.
    * Si el usuario pregunta por accidentes (ej: "¿Qué accidentes hubo hoy?", "¿Accidentes en la calle 72?", "¿Hay trancones por la circunvalar?"), intenta obtener detalles para la búsqueda (fecha, ubicación, tipo de accidente).
    * Si se te provee 'Contexto de la base de datos', úsalo EXCLUSIVAMENTE para responder la pregunta actual del usuario. No lo menciones explícitamente.
    * Si no hay datos o no encuentras nada, infórmalo amablemente (ej: "No encontré registros de accidentes con esos criterios en este momento.").
3.  **Guía y Consejos Viales**: Guiar a los usuarios sobre seguridad vial, normas de tránsito colombianas relevantes, y procedimientos importantes en caso de accidente (qué hacer, a quién llamar como la línea de emergencia 123, policía de tránsito, aseguradora).
4.  **Conversación General Relacionada**: Conversar de manera general y amena sobre temas relacionados con la movilidad, el tráfico, el transporte público y la seguridad vial en Barranquilla.

Capacidades Clave y Comportamiento Esperado:
-   **Lenguaje y Tono**: Usa un español colombiano claro, amigable y respetuoso. Sé paciente y comprensivo.
-   **Clarificación**: Si la pregunta del usuario es ambigua o no la entiendes bien, pide amablemente que la reformule o dé más detalles. No asumas.
-   **Manejo de Información (Veracidad)**: ¡No inventes información! Especialmente sobre accidentes, datos específicos, o procedimientos legales si no tienes la información certera. Es mejor decir "No tengo esa información en este momento, pero te sugiero consultar [fuente oficial]" o "No encontré datos sobre eso."
-   **Concisión y Formato**: Mantén las respuestas razonablemente concisas y bien formateadas para Telegram (usa saltos de línea para legibilidad, emojis con moderación para mejorar la comunicación).
-   **Contexto Local**: Recuerda siempre que estás en Barranquilla, Colombia.
-   **Limitaciones**: Eres un IA. No puedes realizar acciones externas directas (llamar a emergencias, enviar correos, acceder a sistemas externos más allá de la información que se te provea). Tu función es informar y guiar. Sí puedes indicar al usuario qué números llamar o qué acciones tomar.
-   **Uso de Datos Externos**: Si se te proporciona 'Contexto de la base de datos' en un mensaje, úsalo para responder la consulta actual. No lo memorices para futuras preguntas no relacionadas.
-   **Comandos**: Recuerda al usuario los comandos útiles como /reportar, /ayuda, /reset_chat cuando sea apropiado.

Ejemplo de interacción para reporte:
Usuario: "Hubo un choque horrible en la 84"
Tú: "¡Lamento escuchar eso! Espero que todos estén bien. Para poder registrar el accidente, ¿podrías darme una descripción más detallada de lo que pasó, la ubicación lo más exacta posible (ej. Calle 84 con Carrera 50) y cuándo ocurrió? También puedes usar el comando /reportar para un reporte guiado."
"""

async def generate_response(user_id: str, user_message: str, api_data_context: dict = None) -> str:
    """
    Genera una respuesta utilizando el LLM, manteniendo un historial de conversación por usuario.
    """
    if not llm_model: # Verifica si el modelo se inicializó correctamente.
        logger.error(f"LLM_SERVICE: Modelo Gemini no disponible para user_id {user_id}.")
        return "Lo siento, estoy experimentando dificultades técnicas con mi asistente inteligente en este momento. Por favor, intenta de nuevo más tarde."

    # Obtener o inicializar la sesión de chat para el usuario.
    if user_id not in conversation_sessions_store:
        # Inicia una nueva sesión de chat. El historial puede incluir el prompt de sistema.
        # El SDK de Gemini maneja el historial internamente en el objeto ChatSession.
        # El primer mensaje del historial puede ser el prompt de sistema.
        initial_history = [
            {"role": USER_ROLE, "parts": [{"text": SYSTEM_PROMPT_TEXT}]},
            {"role": MODEL_ROLE, "parts": [{"text": "¡Hola! Soy tu Asistente Vial Barranquilla. ¿Cómo puedo ayudarte hoy con la movilidad o algún reporte? 🚦"}]}
        ]
        conversation_sessions_store[user_id] = llm_model.start_chat(history=initial_history)
        logger.info(f"LLM_SERVICE: Nueva sesión de chat iniciada para user_id {user_id}.")
    
    chat_session = conversation_sessions_store[user_id]

    # Preparar el mensaje del usuario, añadiendo contexto de la API si existe (para RAG).
    message_parts_for_llm = [{"text": user_message}]
    if api_data_context:
        # Formatea los datos de la API de manera legible para el LLM.
        # Puedes experimentar con diferentes formatos (JSON, texto descriptivo).
        # Es importante instruir al LLM sobre cómo usar este contexto en el SYSTEM_PROMPT_TEXT.
        context_info_text = (
            "\n\n--- Contexto de la base de datos (para tu información interna al responder la pregunta actual del usuario) ---\n"
            f"{json.dumps(api_data_context, indent=2, ensure_ascii=False)}\n"
            "--- Fin del contexto ---"
        )
        message_parts_for_llm.append({"text": context_info_text})
        logger.debug(f"LLM_SERVICE: Añadiendo contexto de API al mensaje para user_id {user_id}: {context_info_text[:200]}...")

    try:
        logger.debug(f"LLM_SERVICE: Enviando mensaje a Gemini para user_id {user_id}. Mensaje (inicio): {str(message_parts_for_llm)[:300]}...")
        
        # Envía el mensaje al LLM usando la sesión de chat activa.
        # `send_message_async` es preferible en un entorno asyncio.
        llm_api_response = await chat_session.send_message_async(message_parts_for_llm)
        
        # Extrae el texto de la respuesta.
        # El SDK puede tener protecciones o feedback en `response.prompt_feedback`.
        if llm_api_response.prompt_feedback and llm_api_response.prompt_feedback.block_reason:
            block_reason = llm_api_response.prompt_feedback.block_reason
            block_message = f"Respuesta bloqueada por política de seguridad: {block_reason}."
            logger.warning(f"LLM_SERVICE: Respuesta de Gemini bloqueada para user_id {user_id}. Razón: {block_reason}. Feedback: {llm_api_response.prompt_feedback}")
            # Considera qué mensaje enviar al usuario en este caso.
            return f"No pude generar una respuesta completa debido a una restricción de contenido ({block_reason}). Por favor, reformula tu pregunta."

        generated_text = llm_api_response.text
        logger.info(f"LLM_SERVICE: Respuesta recibida de Gemini para user_id {user_id}: {generated_text[:300]}...")

        # El historial en `chat_session.history` es actualizado automáticamente por el SDK.
        # No es necesario truncar manualmente aquí a menos que tengas requisitos muy específicos
        # no cubiertos por la gestión de historial del SDK o si el historial crece demasiado.
        # logger.debug(f"LLM_SERVICE: Historial de chat para user_id {user_id} ahora tiene {len(chat_session.history)} turnos.")

        return generated_text

    except Exception as e:
        logger.error(f"LLM_SERVICE: Error al generar respuesta con Gemini para user_id {user_id}: {e}", exc_info=True)
        # Intenta obtener más detalles del error si es específico de la API de Gemini
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
            logger.error(f"LLM_SERVICE: Prompt Feedback de Gemini en error: {e.response.prompt_feedback}")
        # Considera si reintentar o devolver un mensaje de error genérico.
        return "Lo siento, tuve un problema técnico al intentar procesar tu solicitud con el asistente inteligente. Por favor, intenta de nuevo en unos momentos."


async def classify_intent_and_extract_entities(user_message: str) -> dict:
    """
    (Función Avanzada Opcional) Utiliza el LLM para una tarea específica de clasificación de intención
    y extracción de entidades. Esto se ejecuta fuera del historial de chat principal.
    """
    if not llm_model:
        logger.error("LLM_SERVICE: Modelo Gemini no disponible para clasificación de intención.")
        return {"error": "Modelo Gemini no disponible."}

    # Prompt específico para la tarea de clasificación y extracción.
    # Es crucial que este prompt sea claro y dé ejemplos del formato JSON esperado.
    classification_prompt_text = f"""
    Analiza el siguiente mensaje de usuario y determina su intención principal y extrae entidades relevantes.
    Intenciones posibles: REPORTAR_ACCIDENTE, CONSULTAR_ACCIDENTE, GUIA_VITAL, SALUDO, DESPEDIDA, PREGUNTA_GENERAL, AFIRMACION, NEGACION, CANCELAR_ACCION, DESCONOCIDO.
    
    Para REPORTAR_ACCIDENTE, extrae si es posible: "descripcion" (string), "ubicacion" (string), "fecha" (string), "hora" (string).
    Para CONSULTAR_ACCIDENTE, extrae si es posible: "ubicacion" (string), "fecha" (string), "tipo_accidente" (string), "gravedad" (string).
    
    Mensaje del usuario: "{user_message}"

    Responde ÚNICAMENTE en formato JSON válido con las claves "intent" (string) y "entities" (objeto JSON).
    Si no se extraen entidades, "entities" debe ser un objeto vacío {{}}.
    Si la intención no es clara o no encaja en las categorías, usa "DESCONOCIDO".

    Ejemplos de respuesta JSON esperada:
    Si el usuario dice "quiero reportar un choque feo en la calle 72 con 50 anoche":
    {{
      "intent": "REPORTAR_ACCIDENTE",
      "entities": {{
        "descripcion": "choque feo",
        "ubicacion": "calle 72 con 50",
        "fecha": "anoche"
      }}
    }}

    Si el usuario dice "hola":
    {{
      "intent": "SALUDO",
      "entities": {{}}
    }}
    
    Si el usuario dice "hubo accidentes hoy en la circunvalar?":
    {{
      "intent": "CONSULTAR_ACCIDENTE",
      "entities": {{
        "fecha": "hoy",
        "ubicacion": "la circunvalar"
      }}
    }}
    """
    try:
        logger.debug(f"LLM_SERVICE: Enviando prompt de clasificación/extracción a Gemini (inicio): {classification_prompt_text[:300]}...")
        
        # Para tareas de una sola vez como esta, `generate_content_async` es más directo. No usa historial.
        llm_classification_response = await llm_model.generate_content_async(classification_prompt_text)
        
        # Verificar si la respuesta fue bloqueada.
        if llm_classification_response.prompt_feedback and llm_classification_response.prompt_feedback.block_reason:
            block_reason = llm_classification_response.prompt_feedback.block_reason
            logger.warning(f"LLM_SERVICE: Respuesta de clasificación de Gemini bloqueada. Razón: {block_reason}.")
            return {"intent": "DESCONOCIDO", "entities": {}, "error": f"Respuesta de clasificación bloqueada ({block_reason})", "raw_response": ""}

        raw_json_text = llm_classification_response.text
        logger.info(f"LLM_SERVICE: Respuesta de clasificación (raw JSON) de Gemini: {raw_json_text}")

        # Limpiar y parsear el JSON de la respuesta.
        # El LLM a veces envuelve el JSON en bloques de código (```json ... ```).
        clean_json_text = raw_json_text.strip()
        if clean_json_text.startswith("```json"):
            clean_json_text = clean_json_text[7:-3].strip() # Quita ```json\n y \n```
        elif clean_json_text.startswith("```"):
             clean_json_text = clean_json_text[3:-3].strip() # Quita ```\n y \n```
        
        parsed_response = json.loads(clean_json_text)
        
        # Validar la estructura básica del JSON esperado.
        if not isinstance(parsed_response, dict) or \
           "intent" not in parsed_response or \
           not isinstance(parsed_response.get("intent"), str) or \
           "entities" not in parsed_response or \
           not isinstance(parsed_response.get("entities"), dict):
            raise ValueError("El JSON de respuesta del LLM para clasificación no tiene la estructura esperada (intent/entities).")
            
        logger.info(f"LLM_SERVICE: Intención y entidades extraídas: {parsed_response}")
        return parsed_response

    except json.JSONDecodeError as json_err:
        logger.error(f"LLM_SERVICE: Error al parsear JSON de Gemini para clasificación: {json_err}. Respuesta original: {raw_json_text}", exc_info=True)
        return {"intent": "DESCONOCIDO", "entities": {}, "error": "Error al parsear la estructura de la respuesta del LLM.", "raw_response": raw_json_text}
    except Exception as e:
        logger.error(f"LLM_SERVICE: Error en clasificación de intención con Gemini: {e}", exc_info=True)
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'): # Error específico de la API de Gemini
            logger.error(f"LLM_SERVICE: Prompt Feedback de Gemini (clasificación) en error: {e.response.prompt_feedback}")
        return {"intent": "DESCONOCIDO", "entities": {}, "error": f"Error inesperado durante la clasificación: {type(e).__name__}"}


async def reset_conversation_history(user_id: str) -> bool:
    """
    Limpia/resetea el historial de conversación (sesión de chat) para un usuario específico.
    """
    if user_id in conversation_sessions_store:
        del conversation_sessions_store[user_id] # Elimina la sesión de chat del almacén.
        logger.info(f"LLM_SERVICE: Historial de conversación (sesión de chat de Gemini) reseteado para el usuario {user_id}.")
        return True
    logger.info(f"LLM_SERVICE: No se encontró historial para resetear para el usuario {user_id}.")
    return False


# Archivo: chatbot/api_client.py
# Cliente HTTP asíncrono para interactuar con el backend FastAPI del proyecto.

import httpx # Librería moderna para realizar peticiones HTTP, soporta async.
from chatbot.config import API_BASE_URL # URL base de la API desde la configuración.
from chatbot.bot_logging import logger # Logger de la aplicación.
import json # Para decodificar errores JSON de forma segura y para logging.

# Define un timeout por defecto para las peticiones HTTP.
DEFAULT_HTTP_TIMEOUT = httpx.Timeout(60.0, connect=5.0) # 60s total, 5s para conectar.

async def report_accident_api(accident_payload: dict) -> dict | None:
    """
    Envía los datos de un nuevo accidente a la API del backend.

    Args:
        accident_payload (dict): Un diccionario que debe coincidir con el esquema Pydantic
                                 `AccidenteCreate` (o como lo hayas llamado) en tu backend FastAPI.
                                 Contiene todos los detalles del accidente a reportar.

    Returns:
        dict | None: Un diccionario con la respuesta de la API si la petición fue exitosa
                     (usualmente el objeto del accidente creado, incluyendo su ID),
                     o un diccionario con claves 'error', 'status_code', 'detail' en caso de fallo,
                     o None si ocurre un error muy inesperado no HTTP.
    """
    report_url = f"{API_BASE_URL.rstrip('/')}/accidentes/"
    logger.debug(f"API_CLIENT: Intentando reportar accidente. URL: {report_url}. Payload (inicio): {str(accident_payload)[:200]}...")
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_HTTP_TIMEOUT) as client:
            response = await client.post(report_url, json=accident_payload)
            response.raise_for_status()
            created_accident_data = response.json()
            logger.info(f"API_CLIENT: Accidente reportado exitosamente. Status: {response.status_code}. Respuesta (inicio): {str(created_accident_data)[:200]}...")
            return created_accident_data
    except httpx.HTTPStatusError as e:
        error_detail_message = f"Error del servidor (HTTP {e.response.status_code})."
        try:
            error_response_content = e.response.json()
            if "detail" in error_response_content:
                if isinstance(error_response_content["detail"], list):
                    error_messages = []
                    for err_item in error_response_content["detail"]:
                        field_location = " -> ".join(map(str, err_item.get("loc", ["campo_desconocido"])))
                        error_msg = err_item.get("msg", "Error de validación no especificado.")
                        error_messages.append(f"Campo '{field_location}': {error_msg}")
                    error_detail_message = "; ".join(error_messages) if error_messages else "Errores de validación detallados no disponibles."
                elif isinstance(error_response_content["detail"], str):
                    error_detail_message = error_response_content["detail"]
                else:
                    error_detail_message = str(error_response_content["detail"])
            else:
                error_detail_message = e.response.text if e.response.text else error_detail_message
        except json.JSONDecodeError:
            error_detail_message = e.response.text if e.response.text else f"Error HTTP {e.response.status_code} sin cuerpo de respuesta JSON."
        logger.error(f"API_CLIENT: Error HTTP ({e.response.status_code}) al reportar accidente. Detalle: {error_detail_message}. Respuesta completa (inicio): {e.response.text[:500]}", exc_info=False)
        return {"error": True, "status_code": e.response.status_code, "detail": error_detail_message}
    except httpx.TimeoutException as e:
        logger.error(f"API_CLIENT: Timeout al conectar/comunicar con la API para reportar accidente. URL: {report_url}. Error: {e}", exc_info=True)
        return {"error": True, "status_code": None, "detail": "El servidor tardó demasiado en responder (timeout). Por favor, intenta más tarde."}
    except httpx.RequestError as e:
        logger.error(f"API_CLIENT: Error de red/conexión al reportar accidente. URL: {report_url}. Error: {e}", exc_info=True)
        return {"error": True, "status_code": None, "detail": f"No se pudo conectar con el servidor para reportar el accidente. Verifica tu conexión o contacta a soporte. ({type(e).__name__})"}
    except Exception as e:
        logger.critical(f"API_CLIENT: Error inesperado y crítico en report_accident_api. URL: {report_url}. Error: {e}", exc_info=True)
        return {"error": True, "status_code": None, "detail": f"Ocurrió un error inesperado y crítico al procesar el reporte: {type(e).__name__}."}


async def get_accidents_from_api(params: dict = None) -> list | dict | None: # <--- CORREGIDO AQUÍ: Acepta 'params'
    """
    Consulta la lista de accidentes desde la API del backend, opcionalmente con filtros.

    Args:
        params (dict, optional): Un diccionario con parámetros de filtro que tu API
                                 soporte (ej. fecha, ubicación, gravedad, etc.).
                                 Ej: {"fecha_ocurrencia_dia": "2024-05-20", "gravedad_estimada": "GRAVE"}

    Returns:
        list | dict | None: Una lista de diccionarios (cada uno representando un accidente) si la
                            petición fue exitosa y se encontraron datos.
                            Podría ser un diccionario si la API devuelve paginación.
                            O un diccionario con claves 'error', 'status_code', 'detail' en caso de fallo.
                            O None para errores muy inesperados.
    """
    query_url = f"{API_BASE_URL.rstrip('/')}/accidentes/"
    logger.debug(f"API_CLIENT: Consultando API de accidentes. URL: {query_url}. Filtros: {params}") # <--- CORREGIDO AQUÍ: Usa 'params' para loguear

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_HTTP_TIMEOUT) as client:
            response = await client.get(query_url, params=params) # <--- CORREGIDO AQUÍ: Pasa 'params' a httpx
            response.raise_for_status()
            
            accidents_data_response = response.json()
            logger.info(f"API_CLIENT: Consulta de accidentes exitosa. Status: {response.status_code}. Número de items (si es lista): {len(accidents_data_response) if isinstance(accidents_data_response, list) else 'Respuesta no es lista'}.")
            return accidents_data_response
    except httpx.HTTPStatusError as e:
        error_detail_message = f"Error del servidor (HTTP {e.response.status_code}) al consultar accidentes."
        try:
            error_response_content = e.response.json()
            error_detail_message = error_response_content.get("detail", e.response.text if e.response.text else error_detail_message)
        except json.JSONDecodeError:
            error_detail_message = e.response.text if e.response.text else f"Error HTTP {e.response.status_code} sin cuerpo de respuesta JSON."
        logger.error(f"API_CLIENT: Error HTTP ({e.response.status_code}) al consultar accidentes. Detalle: {error_detail_message}. Respuesta (inicio): {e.response.text[:500]}", exc_info=False)
        return {"error": True, "status_code": e.response.status_code, "detail": error_detail_message}
    except httpx.TimeoutException as e:
        logger.error(f"API_CLIENT: Timeout al consultar API de accidentes. URL: {query_url}. Error: {e}", exc_info=True)
        return {"error": True, "status_code": None, "detail": "El servidor tardó demasiado en responder (timeout) al consultar accidentes."}
    except httpx.RequestError as e:
        logger.error(f"API_CLIENT: Error de red/conexión al consultar API de accidentes. URL: {query_url}. Error: {e}", exc_info=True)
        return {"error": True, "status_code": None, "detail": f"No se pudo conectar con el servidor para consultar accidentes. ({type(e).__name__})"}
    except Exception as e:
        logger.critical(f"API_CLIENT: Error inesperado y crítico en get_accidents_from_api. URL: {query_url}. Error: {e}", exc_info=True)
        return {"error": True, "status_code": None, "detail": f"Ocurrió un error inesperado y crítico al consultar accidentes: {type(e).__name__}."}


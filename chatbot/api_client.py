# chatbot/api_client.py

import requests
import logging
from datetime import datetime

# Importa la URL base desde config. Asegúrate de que la ruta de importación relativa sea correcta
# Si chatbot/ es la raíz, entonces es from .config import ...
# Si chatbot/ está dentro de otra carpeta, asegúrate de la ruta relativa correcta (ej: from ..config import ...)
from .config import API_BASE_URL

logger = logging.getLogger(__name__)

def get_all_accidents():
    """
    Obtiene todos los accidentes desde el endpoint /accidentes/ de la API.
    Retorna una lista de diccionarios de accidentes o None si hay un error.
    """
    api_url = f"{API_BASE_URL}/accidentes/"
    logger.info(f"Llamando a la API: GET {api_url}")

    try:
        # Considera añadir un timeout a las peticiones para evitar que se queden colgadas
        response = requests.get(api_url, timeout=10) # Añade un timeout de 10 segundos
        response.raise_for_status() # Lanza HTTPError para códigos 4xx/5xx
        
        accidentes_data = response.json()
        logger.info(f"API respondió con {len(accidentes_data)} accidentes.")
        return accidentes_data

    except requests.exceptions.Timeout:
        logger.error(f"Tiempo de espera agotado al llamar a la API {api_url}.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al llamar a la API {api_url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado en api_client.get_all_accidents: {e}")
        return None

# --- Función para obtener y formatear los últimos N accidentes ---
def get_and_format_last_n_accidentes(n: int = 10) -> str:
    """
    Obtiene todos los accidentes, selecciona los últimos N y los formatea como texto.
    Retorna un string con el mensaje o un mensaje de error.
    """
    accidentes = get_all_accidents()

    if accidentes is None: # Error en la API durante la llamada a get_all_accidents
        return "Lo siento, no pude comunicarme con la API de accidentes en este momento."

    if not accidentes: # API respondió, pero no hay datos
        return "No hay accidentes registrados en la base de datos."

    # --- Lógica de ordenamiento y selección ---
    # Asegúrate de que la fecha esté en un formato que Python pueda ordenar (datetime)
    # El formato de fecha en tu schema es 'datetime'. Aquí convertimos la cadena a objeto datetime.
    accidentes_con_fecha_dt = []
    for acc in accidentes:
         fecha_str = acc.get('fecha')
         if isinstance(fecha_str, str):
             try:
                 # Intenta parsear la fecha. Asume formato ISO 8601, que FastAPI/Pydantic suelen usar.
                 # Reemplaza 'Z' por '+00:00' para que fromisoformat lo entienda si está presente
                 acc['fecha_dt'] = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                 accidentes_con_fecha_dt.append(acc)
             except ValueError:
                 logger.warning(f"No se pudo parsear la fecha del accidente ID {acc.get('id', 'N/A')}: '{fecha_str}'")
                 # Este accidente no se incluirá en el ordenamiento por fecha si falla el parseo
         else:
             logger.warning(f"Fecha no es un string para accidente ID {acc.get('id', 'N/A')}: {fecha_str}")


    if not accidentes_con_fecha_dt:
         return "Se encontraron accidentes, pero ninguno tiene una fecha válida para ordenar."


    # Ordena por el objeto datetime (los más recientes primero)
    accidentes_ordenados = sorted(accidentes_con_fecha_dt, key=lambda x: x['fecha_dt'], reverse=True)

    # Tomar los últimos N
    ultimos_n = accidentes_ordenados[:n]

    # --- Formatear la respuesta ---
    mensaje = f"Últimos {len(ultimos_n)} Accidentes:\n\n"
    if not ultimos_n:
         return "No se encontraron accidentes recientes con fecha válida."

    for acc in ultimos_n:
        # Formato de la fecha más legible
        fecha_formateada = acc['fecha_dt'].strftime('%Y-%m-%d %H:%M') if 'fecha_dt' in acc else 'Fecha desconocida'
        
        mensaje += f"ID: {acc.get('id', 'N/A')}\n"
        mensaje += f"Fecha: {fecha_formateada}\n"
        # Como mencionamos antes, este endpoint solo trae ID y fecha por defecto.
        # Si modificas tu API para incluir más detalles (tipo, ubicación, etc.) en este endpoint,
        # puedes añadirlos aquí al mensaje leyendo acc.get('nuevo_campo').
        # Ejemplo: mensaje += f"Tipo: {acc.get('tipo_accidente', {}).get('nombre', 'Desconocido')}\n" # Asumiendo que tipo_accidente ahora es un objeto anidado
        mensaje += "--------------------\n"

    return mensaje

# Puedes añadir aquí otras funciones para interactuar con la API
# def get_accident_details(accident_id: int):
#     """Obtiene los detalles de un accidente específico por ID."""
#     api_url = f"{API_BASE_URL}/accidentes/{accident_id}"
#     logger.info(f"Llamando a la API: GET {api_url}")
#     try:
#         response = requests.get(api_url, timeout=10)
#         response.raise_for_status()
#         accident_data = response.json()
#         return accident_data # Retorna el diccionario con los datos del accidente
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error al obtener accidente {accident_id}: {e}")
#         return None # Retorna None si hay error o no se encuentra
#     except Exception as e:
#         logger.error(f"Error inesperado al obtener accidente {accident_id}: {e}")
#         return None

# --- Ejemplo de cómo formatear los detalles de un accidente (si implementas get_accident_details) ---
# def format_accident_details(accident_data: dict) -> str:
#      if not accident_data:
#          return "No se encontró información para ese accidente."
#
#      mensaje = f"Detalles del Accidente ID: {accident_data.get('id', 'N/A')}\n"
#      mensaje += f"Fecha: {accident_data.get('fecha', 'Desconocida')}\n"
#      mensaje += f"Cantidad Víctimas: {accident_data.get('cantidad_victima', 'N/A')}\n"
#      # ... añadir más campos según tu schema AccidenteRead si la API los devuelve ...
#      # Si la API devuelve objetos relacionados anidados (tipo_accidente, ubicacion, etc.)
#      # deberías acceder a ellos:
#      # mensaje += f"Tipo: {accident_data.get('tipo_accidente', {}).get('nombre', 'Desconocido')}\n"
#      # mensaje += f"Ubicación: {accident_data.get('ubicacion', {}).get('complemento', 'Sin detalles')}\n"
#      # ... etc.
#      return mensaje
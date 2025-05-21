# chatbot/api_client.py
import requests
import logging
from .config import API_BASE_URL

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.default_timeout = 30  # CAMBIO: Timeout aumentado a 30 segundos

    def _request(self, method, endpoint, data=None, params=None, headers=None):
        """Método genérico para realizar peticiones a la API."""
        url = f"{self.base_url}{endpoint}"
        try:
            logger.info(f"Realizando petición {method} a {url} con datos: {data} y params: {params}")
            response = requests.request(method, url, json=data, params=params, headers=headers, timeout=self.default_timeout)
            response.raise_for_status()
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                logger.warning(f"La respuesta de {url} no fue JSON válido. Contenido: {response.text[:100]}")
                return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP al llamar a la API {url}: {e.response.status_code} - {e.response.text}")
            try:
                error_details = e.response.json()
                return {"error": True, "status_code": e.response.status_code, "detail": error_details.get("detail", e.response.text)}
            except requests.exceptions.JSONDecodeError:
                return {"error": True, "status_code": e.response.status_code, "detail": e.response.text}
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al llamar a la API {url}")
            return {"error": True, "detail": "La solicitud a la API tardó demasiado en responder."}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al llamar a la API {url}: {e}")
            return {"error": True, "detail": f"Error de conexión con la API: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado en APIClient._request: {e}")
            return {"error": True, "detail": "Ocurrió un error inesperado al procesar la solicitud a la API."}

    def get_accidents(self, limit: int = 10, skip: int = 0):
        """Obtiene una lista de accidentes."""
        params = {"limit": limit, "skip": skip}
        return self._request("GET", "/accidentes/", params=params)

    def report_accident(self, descripcion: str, latitud: float, longitud: float, gravedad: str = "Leve", usuario_id: int = 1):
        """Reporta un nuevo accidente."""
        payload = {
            "descripcion": descripcion,
            "latitud": latitud,
            "longitud": longitud,
            "gravedad": gravedad,
            "usuario_id": usuario_id
        }
        return self._request("POST", "/accidentes/", data=payload)

    def get_accident_detail(self, accident_id: int):
        """Obtiene los detalles de un accidente específico."""
        return self._request("GET", f"/accidentes/{accident_id}")
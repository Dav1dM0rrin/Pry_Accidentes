# chatbot/llm_service.py
import google.generativeai as genai
import logging
import asyncio # Necesario para ejecutar síncrono en un entorno async
from .config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY no está configurada. El servicio LLM no funcionará.")
            self.model = None
            return
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Servicio LLM (Gemini) configurado exitosamente.")
        except Exception as e:
            logger.error(f"Error al configurar Gemini: {e}")
            self.model = None

    async def get_llm_response(self, prompt: str) -> str | None:
        if not self.model:
            logger.error("El modelo LLM no está inicializado.")
            return "Lo siento, no puedo procesar tu solicitud en este momento debido a un problema con el servicio de IA."
        try:
            logger.info(f"Enviando prompt a LLM: '{prompt[:100]}...'")
            # La SDK de google-generativeai puede no tener un método generate_content_async directo
            # para todos los modelos o puede requerir una configuración diferente para asyncio.
            # Si generate_content es bloqueante, la ejecutamos en un executor para no bloquear el loop de PTB.
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            
            if response.parts:
                llm_text_response = response.text
                logger.info(f"Respuesta recibida de LLM: '{llm_text_response[:100]}...'")
                return llm_text_response
            else:
                # ... (manejo de respuesta sin partes, como en la versión anterior)
                if hasattr(response, 'text') and response.text:
                    return response.text
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        return candidate.content.parts[0].text
                logger.error(f"No se pudo extraer texto de la respuesta del LLM. Respuesta: {response}")
                return "No pude obtener una respuesta clara del servicio de IA."
        except Exception as e:
            logger.error(f"Error al interactuar con LLM: {e}", exc_info=True)
            return "Hubo un problema al comunicarme con el servicio de inteligencia artificial."

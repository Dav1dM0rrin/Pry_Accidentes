# Archivo: chatbot/handlers/conversation_states.py
# Define las constantes para los estados de los ConversationHandlers.

# --- Estados Generales de la Aplicación (si los tuvieras) ---
# Podrías tener un estado principal o de selección de acción si tu bot es más complejo.
# Ejemplo:
# SELECTING_ACTION = 0 # Estado inicial o menú principal.

# --- Estados para el Flujo de Reporte de Accidentes (ConversationHandler) ---
# Estos son los pasos (estados) por los que pasa el usuario al reportar un accidente.
# Se usan números enteros secuenciales, pero podrían ser cualquier valor único.

# Estado 0: El usuario ha iniciado el reporte y se le pide la descripción del accidente.
REPORTING_ACCIDENT_DESCRIPTION = 0

# Estado 1: Se ha recibido la descripción, ahora se pide la ubicación del accidente.
REPORTING_ACCIDENT_LOCATION = 1

# Estado 2: Se ha recibido la ubicación, ahora se pregunta si el accidente fue "ahora" o "antes".
REPORTING_ACCIDENT_DATETIME_CHOICE = 2

# Estado 3: Si el accidente fue "antes", se pide la fecha y hora específicas.
REPORTING_ACCIDENT_DATETIME_SPECIFIC = 3

# Estado 4: Se ha recibido la fecha/hora, ahora se pide la gravedad estimada del accidente.
REPORTING_ACCIDENT_GRAVEDAD = 4

# Estado 5: Se ha recibido la gravedad, ahora se muestra un resumen y se pide confirmación final.
REPORTING_ACCIDENT_CONFIRMATION = 5

# (Opcional) Podrías tener un estado para cuando el ConversationHandler termina y vuelve a un menú.
# Si no tienes un menú principal gestionado por un ConversationHandler padre,
# ConversationHandler.END (que es -1) es suficiente para finalizar el flujo.
# Si `map_to_parent` se usa en el ConversationHandler, este estado sería el destino.
# MAIN_MENU_STATE = 6 # Ejemplo

# Nota: ConversationHandler.END es una constante especial (-1) proporcionada por la librería
# python-telegram-bot para indicar el final de una conversación. No necesitas definirla aquí.
# Lo mismo para ConversationHandler.TIMEOUT (-2) si usas timeouts en estados.

# Es buena práctica mantener todos los estados de un ConversationHandler específico
# agrupados o con un prefijo común para mayor claridad, especialmente si tienes múltiples
# ConversationHandlers en tu bot.

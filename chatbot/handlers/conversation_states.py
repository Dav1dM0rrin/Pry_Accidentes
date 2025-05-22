# Archivo: chatbot/handlers/conversation_states.py
# Define las constantes para los estados de los ConversationHandlers.

# --- Estados para el Flujo de Reporte de Accidentes (ConversationHandler) ---
REPORTING_ACCIDENT_DATETIME_CHOICE = 0   # ¿Accidente ahora o antes? / Ingresar fecha-hora
REPORTING_VICTIM_SEX = 1                 # Pedir sexo_victima ("M", "F", "Otro")
REPORTING_VICTIM_AGE = 2                 # Pedir edad_victima (numérico)
REPORTING_VICTIM_COUNT = 3               # Pedir cantidad_victima (numérico)
REPORTING_VICTIM_CONDITION = 4           # Pedir condicion_victima (por opciones) -> ID
REPORTING_ACCIDENT_GRAVITY = 5           # Pedir gravedad_victima (por opciones) -> ID
REPORTING_ACCIDENT_TYPE = 6              # Pedir tipo_accidente (por opciones) -> ID
REPORTING_BARRIO_SELECTION = 7           # Pedir selección de barrio (para ubicacion_id)
REPORTING_ACCIDENT_CONFIRMATION = 8      # Mostrar resumen y pedir confirmación final

# --- Estados para el Flujo de Login (se añadirán en la Parte 2) ---
# AWAITING_USERNAME_LOGIN = 100
# AWAITING_PASSWORD_LOGIN = 101

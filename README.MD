# Pry_Accidentes: Sistema de Gestión y Análisis de Accidentes en Barranquilla

Este proyecto es una aplicación web integral diseñada para registrar, gestionar, visualizar y analizar datos sobre accidentes de tránsito en la ciudad de Barranquilla. Consiste en un backend API, un panel de administración frontend y un chatbot de Telegram para interacción y consulta de datos.

## Arquitectura del Proyecto

El proyecto está dividido en tres componentes principales:

1.  **Backend (FastAPI):**
    * Ubicado en la carpeta `backend/`.
    * Desarrollado con Python y FastAPI.
    * Proporciona una API RESTful para todas las operaciones de datos (CRUD para accidentes, usuarios, autenticación).
    * Utiliza SQLAlchemy como ORM y se conecta a una base de datos MySQL.
    * Incluye autenticación basada en tokens JWT.

2.  **Frontend - Panel de Administración (React):**
    * Ubicado en la carpeta `frontend/my-admin-panel/`.
    * Desarrollado con JavaScript, React y Vite.
    * Permite a los usuarios administradores gestionar datos de accidentes, visualizar estadísticas, administrar usuarios y reportar nuevos incidentes.
    * Consume la API del backend.
    * Estilizado con CSS y Tailwind CSS.

3.  **Chatbot (Telegram):**
    * Ubicado en la carpeta `chatbot/`.
    * Desarrollado con Python y la librería `python-telegram-bot`.
    * Permite a los usuarios interactuar con el sistema a través de Telegram para consultar información sobre accidentes utilizando un modelo de lenguaje (LLM) para interpretar las solicitudes.
    * Se conecta al backend para obtener y enviar datos.

## Características Principales

* **Gestión de Accidentes:** Registrar, visualizar, actualizar y eliminar información detallada de accidentes.
* **Autenticación de Usuarios:** Sistema de login seguro para el panel de administración.
* **Gestión de Usuarios:** Administrar cuentas de usuario para el panel.
* **Visualización de Datos:** Tableros y gráficos (a implementar/mejorar) para analizar tendencias de accidentalidad.
* **Reporte de Accidentes:** Formulario para ingresar nuevos accidentes.
* **Interacción con Chatbot:** Consultas en lenguaje natural sobre datos de accidentes a través de Telegram.
* **Integración con LLM:** El chatbot utiliza un modelo de lenguaje para procesar las solicitudes de los usuarios.

## Requisitos Previos

Asegúrate de tener instalados los siguientes componentes antes de configurar el proyecto:

* Python (versión 3.8 o superior)
* Node.js y npm (o Yarn)
* MySQL (o un motor de base de datos compatible)
* Un token de Bot de Telegram
* Una clave API para el servicio LLM (si es aplicable, por ejemplo, OpenAI)

## Configuración y Ejecución

Sigue las instrucciones específicas dentro de las carpetas de cada componente:

* **Para el Backend:**
    * Navega a la carpeta `backend/`.
    * Crea y activa un entorno virtual:
        ```bash
        python -m venv venv
        source venv/bin/activate  # En Windows: venv\Scripts\activate
        ```
    * Instala las dependencias:
        ```bash
        pip install -r requirements.txt
        ```
    * Configura las variables de entorno: Crea un archivo `.env` en la carpeta `backend/app/` basado en `backend/app/core/config.py` para la base de datos, `SECRET_KEY`, etc.
        Ejemplo de `.env` para el backend:
        ```env
        DATABASE_URL=mysql+mysqlconnector://USER:PASSWORD@HOST:PORT/DATABASE_NAME
        SECRET_KEY=tu_super_secreta_y_larga_llave_aqui
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```
    * Asegúrate de que tu base de datos MySQL esté en funcionamiento y ejecuta el script SQL `accidentes_barrq.sql` para crear las tablas y cargar datos iniciales si es necesario.
    * Inicia el servidor FastAPI (desde la carpeta `backend/`):
        ```bash
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ```
    * La API estará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

* **Para el Frontend (Panel de Administración):**
    * Navega a la carpeta `frontend/my-admin-panel/`.
    * Instala las dependencias:
        ```bash
        npm install
        # o si usas yarn:
        # yarn install
        ```
    * Configura la URL base de la API si es necesario (por defecto apunta a `http://localhost:8000/api/v1/`). Puedes modificar esto en los componentes que realizan llamadas a la API o centralizarlo en un archivo de configuración/servicio.
    * Inicia la aplicación de desarrollo:
        ```bash
        npm run dev
        # o si usas yarn:
        # yarn dev
        ```
    * El panel de administración estará disponible en `http://localhost:5173` (o el puerto que indique Vite).

* **Para el Chatbot:**
    * Navega a la carpeta `chatbot/`.
    * Crea y activa un entorno virtual:
        ```bash
        python -m venv venv
        source venv/bin/activate # En Windows: venv\Scripts\activate
        ```
    * Instala las dependencias:
        ```bash
        pip install -r requirements.txt
        ```
    * Configura las variables de entorno: Crea un archivo `.env` en la carpeta `chatbot/` basado en `chatbot/config.py`.
        Ejemplo de `.env` para el chatbot:
        ```env
        TELEGRAM_BOT_TOKEN=TU_TOKEN_DE_TELEGRAM_BOT
        API_BASE_URL=http://localhost:8000/api/v1  # URL de tu backend
        OPENAI_API_KEY=TU_CLAVE_API_DE_OPENAI_O_SIMILAR # Si usas OpenAI
        # Otras configuraciones del LLM si son necesarias
        ```
    * Ejecuta el bot:
        ```bash
        python bot.py
        ```

## Estructura de la Base de Datos

El esquema de la base de datos se encuentra en el archivo `accidentes_barrq.sql`. Las tablas principales incluyen:

* `autenticacion_usuario`: Almacena la información de los usuarios del panel de administración.
* `accidente_accidente`: Almacena los detalles de los accidentes.
* Otras tablas relacionadas (ej. `tipo_vehiculo`, `clase_accidente`, etc.) para categorizar la información.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue las buenas prácticas de desarrollo, comenta tu código y asegúrate de que las pruebas (si existen) pasen antes de enviar un Pull Request.

## Próximas Mejoras (Roadmap Sugerido)

* Implementación de pruebas unitarias y de integración.
* Mejoras en la visualización de datos en el frontend (gráficos interactivos).
* Refinamiento del procesamiento de lenguaje natural en el chatbot.
* Paginación y filtros más avanzados en el panel de administración.
* Despliegue (Dockerización, configuración de CI/CD).

---

*Este proyecto fue desarrollado como parte de [Menciona el contexto si aplica, ej: un proyecto universitario, iniciativa personal, etc.]*.
*Autor: David Morrín*
*Contacto: [Tu email o forma de contacto preferida]*

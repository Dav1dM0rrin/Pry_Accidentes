import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables desde un archivo .env

class Settings:
    PROJECT_NAME: str = "API FastAPI"
    DATABASE_URL: str = "mysql+pymysql://root@localhost/accidentesbaq"
    SECRET_KEY: str = "clave_super_secreta"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día
    

settings = Settings()


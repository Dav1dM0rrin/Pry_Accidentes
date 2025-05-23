import sys
import os
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from getpass import getpass # Para ingresar la contraseña de forma más segura

# Ajusta la ruta para que Python pueda encontrar tus módulos de la aplicación
# Esto asume que el script está en una carpeta 'scripts' al mismo nivel que 'app'
# Si la estructura es diferente, ajusta esta ruta.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    from app.core.config import settings
    from app.models import modelos # Asegúrate que modelos.py esté accesible
    from app.crud.auth import hash_password # Importa tu función de hash
    from app.database import Base # Si tus modelos heredan de una Base común en database.py
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que el script esté en la ubicación correcta y que PYTHONPATH esté configurado si es necesario.")
    print(f"Project root intentado: {project_root}")
    sys.exit(1)

# Configuración de la base de datos
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_user_password():
    db = SessionLocal()
    try:
        print("--- Actualizar Contraseña de Usuario ---")
        
        identifier_type = input("¿Identificar usuario por 'id' o 'username'? (id/username): ").lower()
        if identifier_type not in ['id', 'username']:
            print("Tipo de identificador no válido.")
            return

        if identifier_type == 'id':
            try:
                user_identifier = int(input("Ingrese el ID del usuario: "))
            except ValueError:
                print("ID no válido. Debe ser un número.")
                return
            user_to_update = db.query(modelos.Usuario).filter(modelos.Usuario.id == user_identifier).first()
        else: # username
            user_identifier = input("Ingrese el username del usuario: ")
            user_to_update = db.query(modelos.Usuario).filter(modelos.Usuario.username == user_identifier).first()

        if not user_to_update:
            print(f"Usuario con {identifier_type} '{user_identifier}' no encontrado.")
            return

        print(f"Usuario encontrado: ID={user_to_update.id}, Username='{user_to_update.username}', Email='{user_to_update.email}'")
        
        # Advertencia sobre la contraseña actual
        print(f"Contraseña actual (puede estar en texto plano o ya hasheada): {user_to_update.password[:20]}...") # Muestra solo una parte

        confirm = input("¿Desea proceder a actualizar la contraseña de este usuario? (s/N): ").lower()
        if confirm != 's':
            print("Operación cancelada.")
            return

        plain_password = getpass("Ingrese la NUEVA contraseña en texto plano para este usuario: ")
        if not plain_password:
            print("La contraseña no puede estar vacía.")
            return
        
        confirm_password = getpass("Confirme la NUEVA contraseña: ")
        if plain_password != confirm_password:
            print("Las contraseñas no coinciden.")
            return

        hashed_new_password = hash_password(plain_password)
        
        user_to_update.password = hashed_new_password
        db.add(user_to_update)
        db.commit()
        
        print(f"¡Contraseña actualizada exitosamente para el usuario '{user_to_update.username}'!")
        print(f"Nuevo hash (parcial): {hashed_new_password[:20]}...")

    except Exception as e:
        db.rollback()
        print(f"Ocurrió un error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Si tus modelos no se crean automáticamente al importar, puedes necesitar esto:
    # Base.metadata.create_all(bind=engine) # Descomentar si es necesario y Base está definida
    
    # Verificar si la tabla de usuarios existe (opcional, pero útil para depurar)
    from sqlalchemy import inspect as sqlalchemy_inspect
    inspector = sqlalchemy_inspect(engine)
    if not inspector.has_table(modelos.Usuario.__tablename__):
        print(f"Error: La tabla '{modelos.Usuario.__tablename__}' no existe en la base de datos.")
        print("Asegúrate de que las migraciones se hayan ejecutado o que los modelos se hayan creado.")
    else:
        update_user_password()
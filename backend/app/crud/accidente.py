# Fastapi_React/Backend/app/crud/accidente.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func 
from app.schemas import schemas
from app.models import modelos, proxy
from app.crud import auth # Asegúrate que auth.py esté en la misma carpeta (crud) o ajusta la importación
from datetime import date
from app.models.proxy import AccidentProxy


# --- ZONA ---
def crear_zona(db: Session, zona: schemas.ZonaBase):
    db_zona = modelos.Zona(**zona.dict())
    db.add(db_zona)
    db.commit()
    db.refresh(db_zona)
    return db_zona

def obtener_zonas(db: Session):
    return db.query(modelos.Zona).all()


# --- TIPO VIA ---
def crear_tipo_via(db: Session, tipo_via: schemas.TipoViaBase):
    db_tipo = modelos.TipoVia(**tipo_via.dict())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

def obtener_tipos_via(db: Session):
    return db.query(modelos.TipoVia).all()


# --- TIPO ACCIDENTE ---
def crear_tipo_accidente(db: Session, tipo: schemas.TipoAccidenteBase):
    db_tipo = modelos.TipoAccidente(**tipo.dict())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

def obtener_tipos_accidente(db: Session):
    return db.query(modelos.TipoAccidente).all()


# --- CONDICION VICTIMA ---
def crear_condicion_victima(db: Session, cond: schemas.CondicionVictimaBase):
    db_cond = modelos.CondicionVictima(**cond.dict())
    db.add(db_cond)
    db.commit()
    db.refresh(db_cond)
    return db_cond

def obtener_condiciones_victima(db: Session):
    return db.query(modelos.CondicionVictima).all()


# --- UBICACION ---
def crear_ubicacion(db: Session, ubic: schemas.UbicacionBase):
    # Aquí podrías necesitar convertir latitud/longitud si vienen como string y el modelo espera float
    # o viceversa, dependiendo de cómo lo manejes finalmente.
    # Por ahora, asume que el schema UbicacionBase ya tiene los tipos correctos para el modelo.
    db_ubic = modelos.Ubicacion(**ubic.dict())
    db.add(db_ubic)
    db.commit()
    db.refresh(db_ubic)
    return db_ubic

def obtener_ubicaciones(db: Session):
    return db.query(modelos.Ubicacion).all()


# --- GRAVEDAD VICTIMA ---
def crear_gravedad_victima(db: Session, grav: schemas.GravedadVictimaBase):
    db_grav = modelos.GravedadVictima(**grav.dict())
    db.add(db_grav)
    db.commit()
    db.refresh(db_grav)
    return db_grav

def obtener_gravedades_victima(db: Session):
    return db.query(modelos.GravedadVictima).all()


# --- BARRIO ---
def crear_barrio(db: Session, barrio: schemas.BarrioBase):
    db_barrio = modelos.Barrio(**barrio.dict())
    db.add(db_barrio)
    db.commit()
    db.refresh(db_barrio)
    return db_barrio

def obtener_barrios(db: Session):
    return db.query(modelos.Barrio).all()


# --- VIA ---
def crear_via(db: Session, via: schemas.ViaBase):
    db_via = modelos.Via(**via.dict())
    db.add(db_via)
    db.commit()
    db.refresh(db_via)
    return db_via

def obtener_vias(db: Session):
    return db.query(modelos.Via).all()


# --- USUARIO ---
# Estas funciones están aquí y no se han borrado.
def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_pwd = auth.hash_password(usuario.password) # Usar la función de hash de auth.py
    db_usuario = modelos.Usuario(
        username=usuario.username,
        email=usuario.email,
        primer_nombre=usuario.primer_nombre,
        primer_apellido=usuario.primer_apellido,
        password=hashed_pwd  # Guardar la contraseña hasheada
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def obtener_usuarios(db: Session):
    return db.query(modelos.Usuario).all()


# --- ACCIDENTE ---
def crear_accidente(db: Session, accidente_data: schemas.AccidenteCreateInput, usuario_id: int):
    db_accidente_data = accidente_data.dict()
    db_accidente_data['usuario_id'] = usuario_id
    db_accidente = modelos.Accidente(**db_accidente_data)
    db.add(db_accidente)
    db.commit()
    db.refresh(db_accidente)
    return db_accidente

def obtener_accidentes(db: Session): # Para listado general, puede no necesitar todas las relaciones
    return db.query(modelos.Accidente).order_by(modelos.Accidente.fecha.desc()).all()

def obtener_accidente(db: Session, accidente_id: int) -> Optional[modelos.Accidente]:
    """
    Obtiene un accidente específico por su ID, cargando todas sus relaciones
    para una vista detallada.
    """
    return db.query(modelos.Accidente).options(
        joinedload(modelos.Accidente.usuario),
        joinedload(modelos.Accidente.tipo_accidente),
        joinedload(modelos.Accidente.condicion_victima),
        joinedload(modelos.Accidente.gravedad), 
        joinedload(modelos.Accidente.ubicacion).joinedload(modelos.Ubicacion.barrio).joinedload(modelos.Barrio.zona),
        joinedload(modelos.Accidente.ubicacion).joinedload(modelos.Ubicacion.primer_via).joinedload(modelos.Via.tipo_via),
        joinedload(modelos.Accidente.ubicacion).joinedload(modelos.Ubicacion.segunda_via).joinedload(modelos.Via.tipo_via)
    ).filter(modelos.Accidente.id == accidente_id).first()

def eliminar_accidente(db: Session, accidente_id: int):
    accidente_obj = obtener_accidente(db, accidente_id) 
    if accidente_obj:
        db.delete(accidente_obj)
        db.commit()
    return accidente_obj

def obtener_accidentes_filtrados_mapa(
    db: Session,
    barrio_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    tipo_accidente_id: Optional[int] = None,
    gravedad_id: Optional[int] = None,
    limit: int = 100 
) -> List[modelos.Accidente]:

    query = db.query(modelos.Accidente).options(
        joinedload(modelos.Accidente.ubicacion).joinedload(modelos.Ubicacion.barrio),
        joinedload(modelos.Accidente.ubicacion).joinedload(modelos.Ubicacion.primer_via),
        joinedload(modelos.Accidente.ubicacion).joinedload(modelos.Ubicacion.segunda_via),
        joinedload(modelos.Accidente.tipo_accidente),
        joinedload(modelos.Accidente.gravedad) 
    )

    if barrio_id is not None:
        # Asegúrate de que el join sea correcto si Accidente.ubicacion_id es la FK a Ubicacion.id
        query = query.join(modelos.Ubicacion, modelos.Accidente.ubicacion_id == modelos.Ubicacion.id)\
                     .filter(modelos.Ubicacion.barrio_id == barrio_id)
    if fecha_desde is not None:
        query = query.filter(modelos.Accidente.fecha >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(modelos.Accidente.fecha <= fecha_hasta)
    if tipo_accidente_id is not None:
        query = query.filter(modelos.Accidente.tipo_accidente_id == tipo_accidente_id)
    if gravedad_id is not None:
        query = query.filter(modelos.Accidente.gravedad_victima_id == gravedad_id)

    query = query.order_by(modelos.Accidente.fecha.desc(), modelos.Accidente.id.desc())
    query = query.limit(limit)
    return query.all()

# --- PROXY ---
proxy = AccidentProxy()
def obtener_proxy(refrescar: bool = False):
    """
    Función que utiliza el proxy para obtener los accidentes.
    El parámetro 'refrescar' fuerza la recarga de datos desde la BD.
    """
    return proxy.obtener_accidentes(refrescar)
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models import modelos
from app.crud import auth

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
def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_pwd = auth.hash_password(usuario.password)
    db_usuario = modelos.Usuario(
        username=usuario.username,
        email=usuario.email,
        primer_nombre=usuario.primer_nombre,
        primer_apellido=usuario.primer_apellido,
        password=hashed_pwd  # Contraseña hasheada
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def obtener_usuarios(db: Session):
    return db.query(modelos.Usuario).all()


# --- ACCIDENTE ---
def crear_accidente(db: Session, accidente: schemas.AccidenteCreate):
    db_accidente = modelos.Accidente(**accidente.dict())
    db.add(db_accidente)
    db.commit()
    db.refresh(db_accidente)
    return db_accidente

def obtener_accidentes(db: Session):
    return db.query(modelos.Accidente).all()

def obtener_accidente(db: Session, accidente_id: int):
    return db.query(modelos.Accidente).filter(modelos.Accidente.id == accidente_id).first()

def eliminar_accidente(db: Session, accidente_id: int):
    accidente = obtener_accidente(db, accidente_id)
    if accidente:
        db.delete(accidente)
        db.commit()
    return accidente



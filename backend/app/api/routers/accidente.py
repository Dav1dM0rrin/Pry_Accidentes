from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import  schemas
from app.crud import accidente
from app import database
from app.models import modelos

router = APIRouter()



# --- ZONA ---
@router.post("/zonas/", response_model=schemas.ZonaBase)
def crear_zona(zona: schemas.ZonaBase, db: Session = Depends(get_db)):
    return accidente.crear_zona(db, zona)

@router.get("/zonas/", response_model=list[schemas.ZonaBase])
def listar_zonas(db: Session = Depends(get_db)):
    return accidente.obtener_zonas(db)


# --- TIPO VIA ---
@router.post("/tipos-via/", response_model=schemas.TipoViaBase)
def crear_tipo_via(tipo_via: schemas.TipoViaBase, db: Session = Depends(get_db)):
    return accidente.crear_tipo_via(db, tipo_via)

@router.get("/tipos-via/", response_model=list[schemas.TipoViaBase])
def listar_tipos_via(db: Session = Depends(get_db)):
    return accidente.obtener_tipos_via(db)


# --- TIPO ACCIDENTE ---
@router.post("/tipos-accidente/", response_model=schemas.TipoAccidenteBase)
def crear_tipo_accidente(tipo_acc: schemas.TipoAccidenteBase, db: Session = Depends(get_db)):
    return accidente.crear_tipo_accidente(db, tipo_acc)

@router.get("/tipos-accidente/", response_model=list[schemas.TipoAccidenteBase])
def listar_tipos_accidente(db: Session = Depends(get_db)):
    return accidente.obtener_tipos_accidente(db)


# --- CONDICION VICTIMA ---
@router.post("/condiciones-victima/", response_model=schemas.CondicionVictimaBase)
def crear_condicion_victima(cond: schemas.CondicionVictimaBase, db: Session = Depends(get_db)):
    return accidente.crear_condicion_victima(db, cond)

@router.get("/condiciones-victima/", response_model=list[schemas.CondicionVictimaBase])
def listar_condiciones_victima(db: Session = Depends(get_db)):
    return accidente.obtener_condiciones_victima(db)


# --- UBICACION ---
@router.post("/ubicaciones/", response_model=schemas.UbicacionBase)
def crear_ubicacion(ubic: schemas.UbicacionBase, db: Session = Depends(get_db)):
    return accidente.crear_ubicacion(db, ubic)

@router.get("/ubicaciones/", response_model=list[schemas.UbicacionBase])
def listar_ubicaciones(db: Session = Depends(get_db)):
    return accidente.obtener_ubicaciones(db)


# --- GRAVEDAD VICTIMA ---
@router.post("/gravedades/", response_model=schemas.GravedadVictimaBase)
def crear_gravedad(grav: schemas.GravedadVictimaBase, db: Session = Depends(get_db)):
    return accidente.crear_gravedad_victima(db, grav)

@router.get("/gravedades/", response_model=list[schemas.GravedadVictimaBase])
def listar_gravedades(db: Session = Depends(get_db)):
    return accidente.obtener_gravedades_victima(db)


# --- BARRIO ---
@router.post("/barrios/", response_model=schemas.BarrioBase)
def crear_barrio(barrio: schemas.BarrioBase, db: Session = Depends(get_db)):
    return accidente.crear_barrio(db, barrio)

@router.get("/barrios/", response_model=list[schemas.BarrioRead]) # Cambiado a BarrioRead
def listar_barrios(db: Session = Depends(get_db)):
    return accidente.obtener_barrios(db)


# --- VIA ---
@router.post("/vias/", response_model=schemas.ViaBase)
def crear_via(via: schemas.ViaBase, db: Session = Depends(get_db)):
    return accidente.crear_via(db, via)

@router.get("/vias/", response_model=list[schemas.ViaBase])
def listar_vias(db: Session = Depends(get_db)):
    return accidente.obtener_vias(db)


# --- USUARIO ---
@router.post("/usuarios/", response_model=schemas.UsuarioRead)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return accidente.crear_usuario(db, usuario)

@router.get("/usuarios/", response_model=list[schemas.UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return accidente.obtener_usuarios(db)


# --- ACCIDENTE ---
@router.post("/accidentes/", response_model=schemas.AccidenteCreate)
def crear_accidente(usuario: schemas.AccidenteCreate, db: Session = Depends(get_db)):
    return accidente.crear_accidente(db, usuario)

@router.get("/accidentes/", response_model=list[schemas.AccidenteRead])
def listar_accidentes(db: Session = Depends(get_db)):
    return accidente.obtener_accidentes(db)

@router.get("/accidentes/{accidente_id}", response_model=schemas.AccidenteRead)
def obtener_accidente(accidente_id: int, db: Session = Depends(get_db)):
    acc = accidente.obtener_accidente(db, accidente_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Accidente no encontrado")
    return acc

@router.delete("/accidentes/{accidente_id}")
def eliminar_accidente(accidente_id: int, db: Session = Depends(get_db)):
    acc = accidente.eliminar_accidente(db, accidente_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Accidente no encontrado")
    return {"mensaje": "Accidente eliminado"}


##------ MAPA ----------###

@router.get("/api/accidentes/mapa", response_model=List[dict])
def obtener_accidentes_mapa(
    barrio_id: Optional[int] = Query(None, description="Filtrar por ID de barrio"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los datos de accidentes para mostrar en el mapa.
    Opcionalmente filtra por barrio.
    """
    # **LLAMADA A LA NUEVA FUNCIÓN RENOMBRADA**
    accidentes = accidente.obtener_accidentes_barrio(db=db, barrio_id=barrio_id)

    resultados = []

    for acc in accidentes:
        ubicacion = acc.ubicacion
        tipo_accidente = acc.tipo_accidente.nombre if acc.tipo_accidente else "Sin tipo"

        if ubicacion and ubicacion.latitud and ubicacion.longitud:
            primer_via_nombre = ubicacion.primer_via.nombre_via if ubicacion.primer_via and ubicacion.primer_via.nombre_via else ""
            segunda_via_nombre = ubicacion.segunda_via.nombre_via if ubicacion.segunda_via and ubicacion.segunda_via.nombre_via else ""

            direccion_partes = []
            if primer_via_nombre:
                direccion_partes.append(primer_via_nombre)
            if segunda_via_nombre:
                direccion_partes.append(f"con {segunda_via_nombre}")

            direccion = " ".join(direccion_partes).strip()
            if not direccion:
                direccion = "Dirección no definida"

            barrio_nombre = ubicacion.barrio.nombre if ubicacion.barrio else "Sin barrio"
            complemento = ubicacion.complemento or "Sin complemento"

            descripcion_parts = [tipo_accidente]
            if direccion != "Dirección no definida":
                 descripcion_parts.append(direccion)
            if barrio_nombre != "Sin barrio":
                 descripcion_parts.append(f"({barrio_nombre})")
            if complemento != "Sin complemento":
                 descripcion_parts.append(complemento)

            descripcion = " - ".join(descripcion_parts)

            try:
                lat = float(ubicacion.latitud)
                lng = float(ubicacion.longitud)
                resultados.append({
                    "id": acc.id,
                    "lat": lat,
                    "lng": lng,
                    "descripcion": descripcion
                })
            except (ValueError, TypeError):
                print(f"Error al procesar lat/lng para accidente {acc.id}: {ubicacion.latitud}, {ubicacion.longitud}")
                pass # Ignorar accidentes con lat/lng inválidos

    return resultados
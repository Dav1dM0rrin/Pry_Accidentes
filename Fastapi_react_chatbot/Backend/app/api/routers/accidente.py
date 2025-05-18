# Fastapi_React/Backend/app/api/routers/accidente.py
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import schemas # Asegúrate que importe schemas
from app.crud import accidente as crud_accidente # Renombrado para claridad
from app.models import modelos
from app.crud.auth import obtener_usuario_actual

router = APIRouter()

# --- ZONA ---
@router.post("/zonas/", response_model=schemas.ZonaRead) # Cambiado a ZonaRead
def crear_zona(zona: schemas.ZonaBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_zona(db, zona)

@router.get("/zonas/", response_model=list[schemas.ZonaRead]) # Cambiado a ZonaRead
def listar_zonas(db: Session = Depends(get_db)):
    return crud_accidente.obtener_zonas(db)


# --- TIPO VIA ---
@router.post("/tipos-via/", response_model=schemas.TipoViaRead) # Cambiado a TipoViaRead
def crear_tipo_via(tipo_via: schemas.TipoViaBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_tipo_via(db, tipo_via)

@router.get("/tipos-via/", response_model=list[schemas.TipoViaRead]) # Cambiado a TipoViaRead
def listar_tipos_via(db: Session = Depends(get_db)):
    return crud_accidente.obtener_tipos_via(db)


# --- TIPO ACCIDENTE ---
@router.post("/tipos-accidente/", response_model=schemas.TipoAccidenteRead) # Cambiado a TipoAccidenteRead
def crear_tipo_accidente(tipo_acc: schemas.TipoAccidenteBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_tipo_accidente(db, tipo_acc)

@router.get("/tipos-accidente/", response_model=list[schemas.TipoAccidenteRead]) # Cambiado a TipoAccidenteRead
def listar_tipos_accidente(db: Session = Depends(get_db)):
    return crud_accidente.obtener_tipos_accidente(db)


# --- CONDICION VICTIMA ---
@router.post("/condiciones-victima/", response_model=schemas.CondicionVictimaRead) # Cambiado a CondicionVictimaRead
def crear_condicion_victima(cond: schemas.CondicionVictimaBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_condicion_victima(db, cond)

@router.get("/condiciones-victima/", response_model=list[schemas.CondicionVictimaRead]) # Cambiado a CondicionVictimaRead
def listar_condiciones_victima(db: Session = Depends(get_db)):
    return crud_accidente.obtener_condiciones_victima(db)


# --- UBICACION ---
@router.post("/ubicaciones/", response_model=schemas.UbicacionRead) # Cambiado a UbicacionRead
def crear_ubicacion(ubic: schemas.UbicacionBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_ubicacion(db, ubic)

@router.get("/ubicaciones/", response_model=list[schemas.UbicacionRead]) # Cambiado a UbicacionRead
def listar_ubicaciones(db: Session = Depends(get_db)):
    return crud_accidente.obtener_ubicaciones(db)


# --- GRAVEDAD VICTIMA ---
@router.post("/gravedades/", response_model=schemas.GravedadVictimaRead) # Cambiado a GravedadVictimaRead
def crear_gravedad(grav: schemas.GravedadVictimaBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_gravedad_victima(db, grav)

@router.get("/gravedades/", response_model=list[schemas.GravedadVictimaRead]) # Cambiado a GravedadVictimaRead
def listar_gravedades(db: Session = Depends(get_db)):
    return crud_accidente.obtener_gravedades_victima(db)


# --- BARRIO ---
@router.post("/barrios/", response_model=schemas.BarrioRead) 
def crear_barrio(barrio: schemas.BarrioBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_barrio(db, barrio)

@router.get("/barrios/", response_model=list[schemas.BarrioRead]) 
def listar_barrios(db: Session = Depends(get_db)):
    return crud_accidente.obtener_barrios(db)


# --- VIA ---
@router.post("/vias/", response_model=schemas.ViaRead) # Cambiado a ViaRead
def crear_via(via: schemas.ViaBase, db: Session = Depends(get_db)):
    return crud_accidente.crear_via(db, via)

@router.get("/vias/", response_model=list[schemas.ViaRead]) # Cambiado a ViaRead
def listar_vias(db: Session = Depends(get_db)):
    return crud_accidente.obtener_vias(db)


# --- USUARIO ---
@router.post("/usuarios/", response_model=schemas.UsuarioRead)
def crear_usuario_endpoint(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)): # Renombrado para evitar conflicto
    return crud_accidente.crear_usuario(db, usuario)

@router.get("/usuarios/", response_model=list[schemas.UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return crud_accidente.obtener_usuarios(db)


# --- ACCIDENTE ---
@router.post("/accidentes/", response_model=schemas.AccidenteRead) 
def crear_accidente_endpoint( 
    accidente_data: schemas.AccidenteCreateInput, 
    db: Session = Depends(get_db),
    usuario_actual: modelos.Usuario = Depends(obtener_usuario_actual) 
):
    return crud_accidente.crear_accidente(db=db, accidente_data=accidente_data, usuario_id=usuario_actual.id)

@router.get("/accidentes/", response_model=list[schemas.AccidenteRead])
def listar_accidentes(db: Session = Depends(get_db)):
    return crud_accidente.obtener_accidentes(db)

@router.get("/accidentes/{accidente_id}", response_model=schemas.AccidenteRead)
def obtener_accidente_endpoint(accidente_id: int, db: Session = Depends(get_db)): 
    acc = crud_accidente.obtener_accidente(db, accidente_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Accidente no encontrado")
    return acc

@router.delete("/accidentes/{accidente_id}")
def eliminar_accidente_endpoint( 
    accidente_id: int,
    db: Session = Depends(get_db),
    # usuario_actual: models.Usuario = Depends(obtener_usuario_actual) # Opcional
    ):
    acc = crud_accidente.eliminar_accidente(db, accidente_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Accidente no encontrado")
    return {"mensaje": "Accidente eliminado"}


##------ MAPA ----------###
@router.get("/api/accidentes/mapa", response_model=List[dict])
def obtener_accidentes_mapa(
    barrio_id: Optional[int] = Query(None, description="Filtrar por ID de barrio"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar por fecha desde (YYYY-MM-DD)"), # NUEVO
    fecha_hasta: Optional[date] = Query(None, description="Filtrar por fecha hasta (YYYY-MM-DD)"), # NUEVO
    tipo_accidente_id: Optional[int] = Query(None, description="Filtrar por ID de tipo de accidente"), # NUEVO
    gravedad_id: Optional[int] = Query(None, description="Filtrar por ID de gravedad"), # NUEVO
    db: Session = Depends(get_db)
):
    """
    Obtiene los datos de accidentes para mostrar en el mapa.
    Opcionalmente filtra por barrio, rango de fechas, tipo de accidente y gravedad.
    """
    # Llamada a la función CRUD actualizada
    accidentes = crud_accidente.obtener_accidentes_filtrados_mapa(
        db=db,
        barrio_id=barrio_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo_accidente_id=tipo_accidente_id,
        gravedad_id=gravedad_id
    )

    resultados = []
    for acc in accidentes:
        ubicacion = acc.ubicacion
        tipo_accidente_nombre = acc.tipo_accidente.nombre if acc.tipo_accidente else "Sin tipo"

        if ubicacion and ubicacion.latitud and ubicacion.longitud:
            primer_via_nombre = ubicacion.primer_via.nombre_via if ubicacion.primer_via and ubicacion.primer_via.nombre_via else ""
            segunda_via_nombre = ubicacion.segunda_via.nombre_via if ubicacion.segunda_via and ubicacion.segunda_via.nombre_via else ""

            direccion_partes = []
            if primer_via_nombre:
                direccion_partes.append(primer_via_nombre)
            if segunda_via_nombre:
                direccion_partes.append(f"con {segunda_via_nombre}")
            direccion = " ".join(direccion_partes).strip() or "Dirección no definida"
            
            barrio_nombre = ubicacion.barrio.nombre if ubicacion.barrio else "Sin barrio"
            complemento = ubicacion.complemento or "Sin complemento"

            # Construcción de la descripción
            descripcion_parts = [f"ID Acc: {acc.id}", tipo_accidente_nombre]
            if direccion != "Dirección no definida":
                 descripcion_parts.append(direccion)
            if barrio_nombre != "Sin barrio":
                 descripcion_parts.append(f"Barrio: {barrio_nombre}")
            if complemento != "Sin complemento":
                 descripcion_parts.append(f"Comp: {complemento}")
            if acc.fecha:
                descripcion_parts.append(f"Fecha: {acc.fecha.strftime('%Y-%m-%d')}")
            if acc.gravedad: # Asumiendo que la relación 'gravedad' existe y tiene 'nivel_gravedad'
                descripcion_parts.append(f"Gravedad: {acc.gravedad.nivel_gravedad}")


            descripcion = " | ".join(descripcion_parts)

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
                pass 
    return resultados

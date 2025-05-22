import logging
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.schemas.schemas import AccidenteRead  # Asegúrate que este esquema usa from_attributes=True

logger = logging.getLogger(__name__)

class AccidentesDB:
    def __init__(self, session):
        self.session = session

    def get_accidentes(self):
        try:
            # Importación local para evitar circularidad
            from app.models.modelos import Accidente, Ubicacion, Via, Barrio
            result = self.session.query(Accidente)\
                .options(
                    joinedload(Accidente.gravedad),
                    joinedload(Accidente.condicion_victima),
                    joinedload(Accidente.ubicacion)
                        .joinedload(Ubicacion.barrio)
                            .joinedload(Barrio.zona),
                    joinedload(Accidente.ubicacion)
                        .joinedload(Ubicacion.primer_via)
                            .joinedload(Via.tipo_via),
                    joinedload(Accidente.ubicacion)
                        .joinedload(Ubicacion.segunda_via)
                            .joinedload(Via.tipo_via)
                )\
                .all()
            logger.debug("Consulta realizada correctamente: %s", result)
            return result
        except Exception as e:
            logger.exception("Error en get_accidentes:")
            raise e

class AccidentProxy:
    def __init__(self):
        self._cache = None

    def obtener_accidentes(self, refrescar: bool = False):
        session = SessionLocal()
        db = AccidentesDB(session)
        try:
            if refrescar or self._cache is None:
                # Convertir las instancias ORM a su representación serializada (por ejemplo, dicionarios)
                registros = db.get_accidentes()
                # Usa el esquema configurado para ORM (asegúrate de tener `from_attributes=True`)
                self._cache = [AccidenteRead.from_orm(reg) for reg in registros]
            else:
                logger.debug("Obteniendo datos desde el caché")
        finally:
            session.close()
        return self._cache
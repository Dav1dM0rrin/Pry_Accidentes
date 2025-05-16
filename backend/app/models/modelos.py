# Fastapi_React/Backend/app/models/modelos.py
from datetime import date
from typing import List, Optional
from sqlalchemy import CHAR, Column, Integer, String, Date, DateTime, ForeignKey, Float # Asegúrate de importar Float si lo usas
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

class Zona(Base):
    __tablename__ = "accidente_zona"
    id: Mapped[int] = mapped_column(primary_key=True, index=True) # PKs son indexadas por defecto, pero explícito
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    barrios: Mapped[List["Barrio"]] = relationship(back_populates="zona") # Relación inversa

class TipoVia(Base):
    __tablename__ = "accidente_tipovia"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    vias: Mapped[List["Via"]] = relationship(back_populates="tipo_via") # Relación inversa

class TipoAccidente(Base):
    __tablename__ = "accidente_tipoaccidente"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    accidentes: Mapped[List["Accidente"]] = relationship(back_populates="tipo_accidente") # Relación inversa

class CondicionVictima(Base):
    __tablename__ = "accidente_condicionvictima"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rol_victima: Mapped[str] = mapped_column(String(100), nullable=False)

    accidentes: Mapped[List["Accidente"]] = relationship(back_populates="condicion_victima") # Relación inversa

class GravedadVictima(Base):
    __tablename__ = "accidente_gravedadvictima"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nivel_gravedad: Mapped[str] = mapped_column(String(100), nullable=False)

    accidentes: Mapped[List["Accidente"]] = relationship(back_populates="gravedad") # Relación inversa

class Barrio(Base):
    __tablename__ = "accidente_barrio"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    zona_id: Mapped[int] = mapped_column(ForeignKey("accidente_zona.id"), nullable=False, index=True) # FK indexada
    
    zona: Mapped["Zona"] = relationship(back_populates="barrios")
    ubicaciones: Mapped[List["Ubicacion"]] = relationship(back_populates="barrio") # Relación inversa

class Via(Base):
    __tablename__ = "accidente_via"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nombre_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sufijo_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo_via_id: Mapped[int] = mapped_column(ForeignKey("accidente_tipovia.id"), nullable=False, index=True) # FK indexada
    
    tipo_via: Mapped["TipoVia"] = relationship(back_populates="vias")
    # Relaciones inversas para ubicaciones
    ubicaciones_como_primera_via: Mapped[List["Ubicacion"]] = relationship(foreign_keys="Ubicacion.primer_via_id", back_populates="primer_via")
    ubicaciones_como_segunda_via: Mapped[List["Ubicacion"]] = relationship(foreign_keys="Ubicacion.segunda_via_id", back_populates="segunda_via")


class Ubicacion(Base):
    __tablename__ = "accidente_ubicacion"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Si cambiaste a Float en la BD, actualiza aquí también. Sino, Pydantic manejará la conversión desde String.
    # Por consistencia con el schema, si el schema espera float, el modelo debería ser float.
    latitud: Mapped[Optional[float]] = mapped_column(Float, nullable=True) 
    longitud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    complemento: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    barrio_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accidente_barrio.id"), nullable=True, index=True) # FK indexada
    primer_via_id: Mapped[int] = mapped_column(ForeignKey("accidente_via.id"), nullable=False, index=True) # FK indexada
    segunda_via_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accidente_via.id"), nullable=True, index=True) # FK indexada
    
    barrio: Mapped[Optional["Barrio"]] = relationship(back_populates="ubicaciones")
    primer_via: Mapped["Via"] = relationship(foreign_keys=[primer_via_id], back_populates="ubicaciones_como_primera_via")
    segunda_via: Mapped[Optional["Via"]] = relationship(foreign_keys=[segunda_via_id], back_populates="ubicaciones_como_segunda_via")
    accidentes: Mapped[List["Accidente"]] = relationship(back_populates="ubicacion") # Relación inversa

class Usuario(Base):
    __tablename__ = "autenticacion_usuario"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True) # Username es bueno indexarlo
    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # Email también, si se usa para login o búsquedas
    password: Mapped[str] = mapped_column(String(100), nullable=False) # No indexar passwords
    primer_nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    primer_apellido: Mapped[str] = mapped_column(String(100), nullable=False)

    accidentes_reportados: Mapped[List["Accidente"]] = relationship(back_populates="usuario") # Relación inversa

class Accidente(Base):
    __tablename__ = "accidente_accidente"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True) # Indexar fecha
    sexo_victima: Mapped[Optional[str]] = mapped_column(CHAR(1), nullable=True)
    edad_victima: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cantidad_victima: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    usuario_id: Mapped[int] = mapped_column(ForeignKey('autenticacion_usuario.id'), index=True) # FK indexada
    condicion_victima_id: Mapped[int] = mapped_column(ForeignKey('accidente_condicionvictima.id'), index=True) # FK indexada
    gravedad_victima_id: Mapped[int] = mapped_column(ForeignKey('accidente_gravedadvictima.id'), index=True) # Indexar gravedad
    tipo_accidente_id: Mapped[int] = mapped_column(ForeignKey('accidente_tipoaccidente.id'), index=True) # Indexar tipo de accidente
    ubicacion_id: Mapped[int] = mapped_column(ForeignKey('accidente_ubicacion.id'), index=True) # Indexar ubicación
    
    usuario: Mapped["Usuario"] = relationship(back_populates="accidentes_reportados")
    condicion_victima: Mapped["CondicionVictima"] = relationship(back_populates="accidentes")
    gravedad: Mapped["GravedadVictima"] = relationship(back_populates="accidentes")
    tipo_accidente: Mapped["TipoAccidente"] = relationship(back_populates="accidentes")
    ubicacion: Mapped["Ubicacion"] = relationship(back_populates="accidentes")


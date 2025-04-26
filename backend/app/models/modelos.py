from datetime import date
from typing import Optional
from sqlalchemy import CHAR, Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship


Base = declarative_base()

class Zona(Base):
    __tablename__ = "accidente_zona"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

class TipoVia(Base):
    __tablename__ = "accidente_tipovia"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

class TipoAccidente(Base):
    __tablename__ = "accidente_tipoaccidente"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

class CondicionVictima(Base):
    __tablename__ = "accidente_condicionvictima"
    id: Mapped[int] = mapped_column(primary_key=True)
    rol_victima: Mapped[str] = mapped_column(String(100), nullable=False)

class GravedadVictima(Base):
    __tablename__ = "accidente_gravedadvictima"
    id: Mapped[int] = mapped_column(primary_key=True)
    nivel_gravedad: Mapped[str] = mapped_column(String(100), nullable=False)

class Barrio(Base):
    __tablename__ = "accidente_barrio"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    zona_id: Mapped[int] = mapped_column(ForeignKey("accidente_zona.id"), nullable=False)
    zona: Mapped["Zona"] = relationship("Zona")

class Via(Base):
    __tablename__ = "accidente_via"
    id: Mapped[int] = mapped_column(primary_key=True)
    numero_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nombre_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sufijo_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo_via_id: Mapped[int] = mapped_column(ForeignKey("accidente_tipovia.id"), nullable=False)
    tipo_via: Mapped["TipoVia"] = relationship("TipoVia")

class Ubicacion(Base):
    __tablename__ = "accidente_ubicacion"
    id: Mapped[int] = mapped_column(primary_key=True)
    latitud: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    longitud: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    complemento: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    barrio_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accidente_barrio.id"), nullable=True)
    primer_via_id: Mapped[int] = mapped_column(ForeignKey("accidente_via.id"), nullable=False)
    segunda_via_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accidente_via.id"), nullable=True)
    barrio: Mapped[Optional["Barrio"]] = relationship("Barrio", foreign_keys=[barrio_id])
    primer_via: Mapped["Via"] = relationship("Via", foreign_keys=[primer_via_id])
    segunda_via: Mapped[Optional["Via"]] = relationship("Via", foreign_keys=[segunda_via_id])

class Usuario(Base):
    __tablename__ = "autenticacion_usuario"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    primer_nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    primer_apellido: Mapped[str] = mapped_column(String(100), nullable=False)

class Accidente(Base):
    __tablename__ = "accidente_accidente"
    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(nullable=False)
    sexo_victima: Mapped[Optional[str]] = mapped_column(CHAR(1), nullable=True)
    edad_victima: Mapped[Optional[int]] = mapped_column(nullable=True)
    cantidad_victima: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    usuario_id: Mapped[int] = mapped_column(ForeignKey('autenticacion_usuario.id'))
    usuario: Mapped["Usuario"] = relationship("Usuario")

    condicion_victima_id: Mapped[int] = mapped_column(ForeignKey('accidente_condicionvictima.id'))
    condicion_victima: Mapped["CondicionVictima"] = relationship("CondicionVictima")

    gravedad_victima_id: Mapped[int] = mapped_column(ForeignKey('accidente_gravedadvictima.id'))
    gravedad: Mapped["GravedadVictima"] = relationship("GravedadVictima")

    tipo_accidente_id: Mapped[int] = mapped_column(ForeignKey('accidente_tipoaccidente.id'))
    tipo_accidente: Mapped["TipoAccidente"] = relationship("TipoAccidente")

    ubicacion_id: Mapped[int] = mapped_column(ForeignKey('accidente_ubicacion.id'))
    ubicacion: Mapped["Ubicacion"] = relationship("Ubicacion")

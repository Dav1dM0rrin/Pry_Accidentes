from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime

from sqlalchemy import CHAR



class LoginRequest(BaseModel):
    username: str
    password: str



# ----------- TOKENS ------------ #

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ----------- MODELOS BÁSICOS ------------ #

class ZonaBase(BaseModel):
    nombre: str

class TipoViaBase(BaseModel):
    nombre: str

class TipoAccidenteBase(BaseModel):
    nombre: str

class CondicionVictimaBase(BaseModel):
    rol_victima: str

class UbicacionBase(BaseModel):
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    complemento: Optional[str] = None
    barrio_id: int
    primer_via_id: int
    segunda_via_id: Optional[int] = None
    


class GravedadVictimaBase(BaseModel):
    nivel_gravedad: str

class BarrioBase(BaseModel):
    nombre: str
    zona_id: int

class ViaBase(BaseModel):
    numero_via: Optional[str] = None
    nombre_via:Optional[str] = None
    sufijo_via: Optional[str] = None   ## EL OPTIONAL[] = none  ES PARA QUE SEA NULO 
    tipo_via_id: int

class UsuarioBase(BaseModel):
    username: str

class UsuarioCreate(UsuarioBase):
    username: str
    password: str
    email:str
    primer_nombre:str
    primer_apellido:str

class UsuarioRead(UsuarioBase):
    id: int
    email: str
    primer_nombre: str
    primer_apellido: str

    class Config:
        orm_mode = True


# ----------- MODELO ACCIDENTE ------------ #

class AccidenteBase(BaseModel):
  fecha:datetime
  sexo_victima:Optional[str]=None
  edad_victima:Optional[int]=None
  cantidad_victima:Optional[int]=None
  usuario_id:int
  condicion_victima_id:int
  gravedad_victima_id:int
  tipo_accidente_id:int
  ubicacion_id:int
  

class AccidenteCreate(AccidenteBase):
    fecha:datetime
    sexo_victima:Optional[str]=None
    edad_victima:Optional[int]=None
    cantidad_victima:Optional[int]=None
    usuario_id:int
    condicion_victima_id:int
    gravedad_victima_id:int
    tipo_accidente_id:int
    ubicacion_id:int

class AccidenteRead(AccidenteBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2

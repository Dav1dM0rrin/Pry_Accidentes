# Fastapi_React/Backend/app/schemas/schemas.py
from pydantic import BaseModel, validator # validator no se usa aquí, se puede quitar si no es necesario
from typing import Optional
from datetime import date, datetime
# from decimal import Decimal # No es necesario importar Decimal si usamos float

# ... (LoginRequest, Token, TokenData sin cambios) ...

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ----------- MODELOS BÁSICOS READ (con ID) ------------ #

class ZonaBase(BaseModel):
    nombre: str

class ZonaRead(ZonaBase):
    id: int
    class Config:
        from_attributes = True


class TipoViaBase(BaseModel):
    nombre: str

class TipoViaRead(TipoViaBase):
    id: int
    class Config:
        from_attributes = True


class TipoAccidenteBase(BaseModel):
    nombre: str

class TipoAccidenteRead(TipoAccidenteBase):
    id: int
    class Config:
        from_attributes = True


class CondicionVictimaBase(BaseModel):
    rol_victima: str

class CondicionVictimaRead(CondicionVictimaBase):
    id: int
    class Config:
        from_attributes = True

class BarrioBase(BaseModel):
    nombre: str
    zona_id: int

class BarrioRead(BarrioBase):
    id: int
    zona: Optional[ZonaRead] = None 
    class Config:
        from_attributes = True

class ViaBase(BaseModel):
    numero_via: Optional[str] = None
    nombre_via:Optional[str] = None
    sufijo_via: Optional[str] = None
    tipo_via_id: int

class ViaRead(ViaBase):
    id: int
    tipo_via: Optional[TipoViaRead] = None 
    class Config:
        from_attributes = True

class UbicacionBase(BaseModel):
    # Cambiar latitud y longitud a Optional[float]
    latitud: Optional[float] = None 
    longitud: Optional[float] = None
    complemento: Optional[str] = None
    barrio_id: Optional[int] = None 
    primer_via_id: int
    segunda_via_id: Optional[int] = None

class UbicacionRead(UbicacionBase):
    id: int
    barrio: Optional[BarrioRead] = None 
    primer_via: Optional[ViaRead] = None 
    segunda_via: Optional[ViaRead] = None 
    class Config:
        from_attributes = True
    

class GravedadVictimaBase(BaseModel):
    nivel_gravedad: str

class GravedadVictimaRead(GravedadVictimaBase):
    id: int
    class Config:
        from_attributes = True


class UsuarioBase(BaseModel):
    username: str

class UsuarioCreate(UsuarioBase):
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
        from_attributes = True


# ----------- MODELO ACCIDENTE ------------ #

class AccidenteBase(BaseModel):
  fecha: datetime 
  sexo_victima: Optional[str] = None
  edad_victima: Optional[int] = None
  cantidad_victima: Optional[int] = None
  condicion_victima_id: int
  gravedad_victima_id: int
  tipo_accidente_id: int
  ubicacion_id: int
  

class AccidenteCreateInput(AccidenteBase):
    pass


class AccidenteCreate(AccidenteBase): 
    usuario_id: int


class AccidenteRead(AccidenteBase): 
    id: int
    usuario_id: int 
    
    usuario: Optional[UsuarioRead] = None
    tipo_accidente: Optional[TipoAccidenteRead] = None
    condicion_victima: Optional[CondicionVictimaRead] = None
    gravedad: Optional[GravedadVictimaRead] = None 
    ubicacion: Optional[UbicacionRead] = None
    
    class Config:
        from_attributes = True

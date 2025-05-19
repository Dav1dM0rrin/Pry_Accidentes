from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.crud.auth import autenticar_usuario, crear_token, obtener_usuario_actual, verificar_password
from app.schemas.schemas import LoginRequest, Token, UsuarioRead
from app.database import get_db
from app.models import modelos

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Acceso a las credenciales de usuario desde el JSON enviado
    usuario = autenticar_usuario(db, login_data.username, login_data.password)
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = crear_token(data={"sub": usuario.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioRead)
def get_usuario_actual(usuario = Depends(obtener_usuario_actual)):
    return usuario



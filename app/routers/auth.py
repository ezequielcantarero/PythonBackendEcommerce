from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.config.database import get_session
from app.models.user_sql import User
from app.utils import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # Usa form-data estándar
    db: AsyncSession = Depends(get_session)
):
    # 1. Buscar usuario por email (en el form_data.username viene el email)
    # Nota: OAuth2 siempre usa el campo "username" aunque nosotros usemos email.
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().one_or_none()

    # 2. Validar usuario y contraseña
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas (Usuario no existe)")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas (Password mal)")

    # 3. Crear el Token JWT
    # Guardamos el ID del usuario en el token ("sub")
    access_token = create_access_token(subject=user.email) # O user.id si prefieres
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_role": user.role # Extra útil para el frontend
    }
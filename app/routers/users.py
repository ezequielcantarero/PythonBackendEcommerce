from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_sql import User
from app.config.database import get_session
from app.utils import hash_password

router = APIRouter(prefix="/users", tags=["Usuarios (SQL)"])

# DTO (Data Transfer Object): Modelo solo para recibir datos del registro
# Lo definimos aquí rápido, aunque idealmente iría en schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("/", response_model=User)
async def create_user(user_input: UserCreate, db: AsyncSession = Depends(get_session)):
    # 1. Validar que el email no exista ya
    # Nota: SQLModel usa sintaxis moderna (exec + one_or_none)
    query = select(User).where(User.email == user_input.email)
    result = await db.execute(query)
    existing_user = result.scalars().one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # 2. Encriptar la contraseña
    hashed_pwd = hash_password(user_input.password)
    
    # 3. Crear la instancia del modelo User (SQL)
    new_user = User(
        username=user_input.username,
        email=user_input.email,
        hashed_password=hashed_pwd,
        role="customer"
    )
    
    # 4. Guardar en Postgres
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) # Recarga el objeto con el ID generado por la DB
    
    return new_user
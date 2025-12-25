from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_session
from app.models.user_sql import User
from app.utils import ALGORITHM, JWT_SECRET_KEY

# Esto le dice a FastAPI: "El token lo sacas de esta URL"
# Así aparecerá el candadito en Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decodificamos el token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. Buscamos al usuario en la DB (por seguridad extra)
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user

    async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Esta función hace 2 cosas:
    1. Llama a get_current_user para validar el token.
    2. Verifica si el rol es 'admin'.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # 403: Prohibido (sabemos quién eres, pero no puedes pasar)
            detail="No tienes permisos de administrador para realizar esta acción"
        )
    return current_user
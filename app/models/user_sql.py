import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users" # Nombre explícito de la tabla en Postgres

    # ID: Usamos UUID para que sea único y seguro (no adivinable como 1, 2, 3...)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    
    # Datos básicos
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True) # unique=True impide emails duplicados
    
    # Seguridad
    hashed_password: str # Aquí guardaremos la contraseña encriptada, NUNCA texto plano
    
    # Roles y Estado
    role: str = Field(default="customer") # "customer" o "admin"
    is_active: bool = Field(default=True)
    
    # Auditoría (Cuándo se creó)
    created_at: datetime = Field(default_factory=datetime.utcnow)
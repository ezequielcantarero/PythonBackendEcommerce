import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.user_sql import User
from app.models.product_mongo import Product
from app.models.order_sql import Order, OrderItem

# 1. Cargar variables de entorno (necesitas python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# --- CONFIG SQL (Postgres) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True) # echo=True para ver logs de SQL para PROD echo=False

# Dependencia para inyectar la sesión SQL en los endpoints
async def get_session():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# --- CONFIG NOSQL (Mongo) ---
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# --- LIFESPAN (Arranque y Cierre) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # INICIO
    print("🚀 Iniciando Motores...")
    
    # A. Iniciar SQL: Crea las tablas si no existen
    async with engine.begin() as conn:
        # Nota: Aquí importaremos los modelos SQL luego para que los detecte
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ PostgreSQL Conectado y Tablas creadas")

    # B. Iniciar Mongo: Conecta Beanie
    client = AsyncIOMotorClient(MONGO_URI)
    # Nota: document_models lista los modelos de Mongo (está vacío por ahora)
    await init_beanie(database=client[MONGO_DB_NAME], document_models=[Product])
    print("✅ MongoDB Conectado")
    
    yield # Aquí corre la app
    
    # CIERRE (Opcional)
    print("🛑 Apagando motores...")
from fastapi import FastAPI
from app.config.database import lifespan
from app.routers import products
from app.routers import users
from app.routers import auth
from app.routers import orders
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hybrid Ecommerce API",
    version="1.0.0",
    lifespan=lifespan # ¡Aquí conectamos las DBs!
)

origins = [
    "http://localhost:5173", # Puerto por defecto de Vite (React moderno)
    "http://localhost:3000", # Puerto clásico de React
    "http://localhost:8080", # Si usas python http.server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # En desarrollo usamos "*" para permitir a TODOS.
                             # En producción, pondrías la lista 'origins' de arriba.
    allow_credentials=True,
    allow_methods=["*"],     # Permitir todos los métodos (GET, POST, PUT, DELETE...)
    allow_headers=["*"],     # Permitir todos los headers (Authorization, etc.)
)

app.include_router(products.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(orders.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a tu API Híbrida (SQL + Mongo)"}
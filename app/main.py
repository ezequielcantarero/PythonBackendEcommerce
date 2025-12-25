from fastapi import FastAPI
from app.config.database import lifespan
from app.routers import products
from app.routers import users
from app.routers import auth

app = FastAPI(
    title="Hybrid Ecommerce API",
    version="1.0.0",
    lifespan=lifespan # ¡Aquí conectamos las DBs!
)

app.include_router(products.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a tu API Híbrida (SQL + Mongo)"}
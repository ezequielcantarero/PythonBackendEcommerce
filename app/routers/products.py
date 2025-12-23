from fastapi import APIRouter, HTTPException
from typing import List
from app.models.product_mongo import Product

# Prefix="/products" significa que todas las rutas empezarán con /products
router = APIRouter(prefix="/products", tags=["Productos (Mongo)"])

# 1. CREAR PRODUCTO (POST)
@router.post("/", response_model=Product)
async def create_product(product: Product):
    # ¡Mira qué fácil es guardar en Mongo con Beanie!
    # No hace falta "insert_one" ni diccionarios raros.
    await product.create() 
    return product

# 2. LISTAR PRODUCTOS (GET)
@router.get("/", response_model=List[Product])
async def list_products():
    # Trae todos los productos y conviértelos a una lista
    products = await Product.find_all().to_list()
    return products

# 3. BUSCAR POR ID (GET)
@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product
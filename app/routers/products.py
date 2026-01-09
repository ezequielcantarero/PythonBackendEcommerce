import shutil
import uuid
import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from app.models.product_mongo import Product
from app.models.user_sql import User
from app.dependencies import get_current_user, get_current_admin

# Prefix="/products" significa que todas las rutas empezarán con /products
router = APIRouter(prefix="/products", tags=["Productos (Mongo)"])

# 1. CREAR PRODUCTO (POST)
@router.post("/", response_model=Product)
async def create_product(product: Product, current_user: User = Depends(get_current_admin)):

    # ¡Mira qué fácil es guardar en Mongo con Beanie!
    # No hace falta "insert_one" ni diccionarios raros.
    await product.create() 
    return product

@router.post("/{product_id}/upload-image", response_model=Product)
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...), # Recibimos el archivo
    current_user: User = Depends(get_current_admin) # Solo Admin puede subir fotos
):
    # 1. Buscar el producto
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 2. Crear un nombre único para el archivo (ej: "a1b2c3d4.jpg")
    # Usamos uuid para que nunca se repita el nombre
    extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{extension}"
    
    # 3. Definir la ruta donde se guardará
    file_location = f"static/images/{unique_filename}"
    
    # 4. Guardar el archivo físicamente en el disco
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 5. Guardar la URL en la base de datos (Mongo)
    # Generamos la URL completa para que el frontend la use directo
    product.image_url = file_location # Ojo: Guardamos la ruta relativa
    await product.save()
    
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
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from sqlmodel import select, SQLModel 
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_session
from app.models.user_sql import User
from app.models.order_sql import Order, OrderItem
from app.models.product_mongo import Product
from app.dependencies import get_current_user, get_current_admin    
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["Pedidos (Híbrido)"])

# --- SCHEMAS (DTOs) ---
# Solo para recibir los datos del frontend (qué producto y cuántos)
class ItemInput(BaseModel):
    product_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[ItemInput]

# ✅ FORMA CORRECTA: Definimos los campos explícitamente
class OrderReadWithItems(SQLModel):
    id: uuid.UUID
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItem]

# Schema para validar el cambio de estado
class OrderStatusUpdate(BaseModel):
    status: str # Ej: "enviado", "entregado", "cancelado"

# --- ENDPOINT DE COMPRA ---
@router.post("/", response_model=Order)
async def create_order(
    order_input: OrderCreate,
    current_user: User = Depends(get_current_user), # Requiere estar logueado
    db: AsyncSession = Depends(get_session)
):
    # 1. Crear la cabecera de la orden (aún sin total ni items)
    new_order = Order(user_id=current_user.id, total_amount=0.0)
    db.add(new_order)
    
    # Hacemos flush para que Postgres genere el ID de la orden (new_order.id) 
    # sin confirmar la transacción todavía.
    await db.flush() 

    total_acumulado = 0.0

    # 2. Iterar sobre los items solicitados
    for item in order_input.items:
        # A. BUSCAR EN MONGO (Lectura)
        product = await Product.get(item.product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"No hay stock suficiente para {product.name}")

        # B. ACTUALIZAR MONGO (Escritura - Restar Stock)
        product.stock -= item.quantity
        await product.save() 

        # C. CREAR ITEM EN SQL (Snapshot de precio y nombre)
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=str(product.id),
            product_name=product.name, # Guardamos el nombre por si cambia después
            price=product.price,       # Guardamos el precio al momento de la compra
            quantity=item.quantity
        )
        db.add(order_item)
        
        total_acumulado += product.price * item.quantity

    # 3. Actualizar el total de la orden y confirmar todo
    new_order.total_amount = total_acumulado
    db.add(new_order) # Actualizamos el objeto orden con el total real
    
    await db.commit() # ¡Aquí se guarda todo en SQL!
    await db.refresh(new_order)
    
    return new_order

# GET: Traer el historial de compras del usuario logueado
@router.get("/", response_model=List[OrderReadWithItems])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Traemos las ordenes DEL usuario actual Y cargamos sus items
    query = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .options(selectinload(Order.items)) # <--- Magia: Carga los detalles (items)
    )
    result = await db.execute(query)
    return result.scalars().all()

# 2. Agrega este endpoint AL FINAL del archivo
@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: uuid.UUID,
    status_input: OrderStatusUpdate,
    current_user: User = Depends(get_current_admin), # <--- ¡CANDADO ROJO! Solo Admins
    db: AsyncSession = Depends(get_session)
):
    # Buscar la orden
    order = await db.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    # Actualizar el estado
    order.status = status_input.status
    
    # Guardar en SQL
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return order
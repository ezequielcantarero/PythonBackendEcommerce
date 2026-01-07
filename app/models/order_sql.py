import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.user_sql import User

# --- TABLA DETALLE (Items del pedido) ---
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    id: int = Field(default=None, primary_key=True)
    
    # Relación con la cabecera del pedido
    order_id: uuid.UUID = Field(foreign_key="orders.id")
    
    # EL ENLACE HÍBRIDO: Guardamos el ID de Mongo como string
    product_id: str = Field(index=True) 
    
    # Guardamos el nombre y precio AQUÍ también (Snapshot).
    # ¿Por qué? Si mañana cambias el precio en Mongo, el pedido viejo no debe cambiar.
    product_name: str
    price: float
    quantity: int

    # Relación inversa (opcional, para navegar desde el item a la orden)
    order: "Order" = Relationship(back_populates="items")


# --- TABLA CABECERA (El Pedido) ---
class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Quién compró (Relación SQL pura)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    
    # Totales
    total_amount: float
    status: str = Field(default="pending") # pending, paid, shipped
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones para navegar en el código
    # user: Optional[User] = Relationship() # Descomenta si quieres acceder a order.user
    items: List[OrderItem] = Relationship(back_populates="order")
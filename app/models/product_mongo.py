from typing import Optional, List
from beanie import Document
from pydantic import Field
from datetime import datetime

class Product(Document):
    # En Mongo no definimos "Tablas", definimos "Colecciones"
    # Beanie usará el nombre de la clase para la colección, o lo definimos abajo.

    name: str
    description: Optional[str] = None
    price: float
    stock: int
    
    # Aquí está la magia de NoSQL: Arrays y estructuras anidadas fáciles
    tags: List[str] = []  # Ej: ["oferta", "verano", "nuevo"]
    
    # Flexibilidad: Podríamos agregar un dict para detalles específicos
    # Ej: {"talla": "M", "color": "rojo"} o {"ram": "16GB", "cpu": "i7"}
    attributes: dict = {} 

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products" # Nombre de la colección en Mongo
from pydantic import BaseModel

class Appliance(BaseModel):
    name: str
    description: str | None
    brand: str
    category: str
    price: float
    quantity_in_stock: int
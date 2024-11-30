from pydantic import BaseModel

class Reservation(BaseModel):
    reservation_date: str
    end_date: str
    status: str

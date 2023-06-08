from pydantic import BaseModel, Field
from typing import Optional

class OrderSchema(BaseModel):
    id: Optional[int]
    quantity: int
    pizza_size: str
    order_status: Optional[str] = "PENDING" 
    user_id: Optional[int]

    class Config:
        orm_mode = True
    
class OrderRequest(BaseModel):
    quantity: int
    pizza_size: str = "SMALL"

# class OrderSchema(BaseModel):
#     id: Optional[int]
#     quantity: int
#     order_status: Optional[str] = Field(default="PENDING")
#     pizza_size: Optional[str] = Field(default="SMALL")
#     user_id: Optional[int]

#     class Config:
#         orm_mode = True
#         schema_extra = {
#             "example": {
#                 "quantity": 2,
#                 "pizza_size": "LARGE"
#             }
#         }


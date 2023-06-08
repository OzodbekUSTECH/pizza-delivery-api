
from pydantic import BaseModel, Field
from typing import Optional

class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "example_user",
                "email": "example@example.com",
                "password": "examplepassword"
            }
        }


class SignUpSchema(BaseModel):
    id: Optional[int]
    username: str
    email: str
    # password: str
    is_staff: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)

    class Config:
        orm_mode = True


class Settings(BaseModel):
    authjwt_secret_key: str = "9e795d50a58bdc911877f9d845117f76501d2135e46ae444509bb42de4ed56af"


class LoginSchema(BaseModel):
    username: str
    password: str



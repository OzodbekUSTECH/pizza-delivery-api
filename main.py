from fastapi import FastAPI
from routers.auth_routes import auth_router
from routers.order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from schemas.auth import Settings

app = FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_router)
app.include_router(order_router)


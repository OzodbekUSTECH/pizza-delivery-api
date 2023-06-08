from fastapi import APIRouter, HTTPException, status, Depends
from db.database import Session, engine
from schemas.auth import SignUpSchema, SignUpRequest, LoginSchema
import models
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

db = Session(bind=engine)

@auth_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    return {"message": "Hello"}

@auth_router.post('/signup', response_model=SignUpSchema, status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpRequest):
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with the email already exists!")

    db_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with the username already exists!")
    
    new_user = models.User(**user.dict())
    new_user.password = generate_password_hash(user.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

#login route

@auth_router.post('/login', status_code=200)
async def login(user: LoginSchema, Authorize: AuthJWT = Depends()):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)
        
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

        
#refreshing tokens
@auth_router.get('/refresh')
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid refresh token")
    current_user = Authorize._get_jwt_identifier()
    
    access_token = Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access": access_token})

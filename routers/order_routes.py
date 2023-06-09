from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
import models
from schemas.order import OrderSchema, OrderRequest, OrderStatusSchema, UserOrdersSchema, DeletedOrderSchema
from db.database import Session, engine
from fastapi.encoders import jsonable_encoder
order_router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)
db = Session(bind=engine)
@order_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token")
    return {"message": "hello"}


@order_router.post('/order', response_model=OrderSchema)
async def place_an_order(order: OrderRequest, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(models.User).filter(models.User.username == current_user).first()

    new_order = models.Order(
        quantity=order.quantity,
        pizza_size=order.pizza_size
    )
    new_order.user_id = user.id
    # new_order.user=user

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    response = {
        "id": new_order.id,
        "quantity": new_order.quantity,
        "order_status": new_order.order_status.value,
        "pizza_size": new_order.pizza_size.value,
        "user_id": new_order.user_id,
    }
    # response = {
    #     "id": new_order.id,
    #     "quantity": new_order.quantity,
    #     "order_status": new_order.order_status,
    #     "pizza_size": new_order.pizza_size,
    # }
    # return jsonable_encoder(response)
    return response
    


@order_router.get('/orders', response_model=list[OrderSchema])
async def list_all_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()

    if user.is_staff:
        # orders = db.query(models.Order).all()
        # return jsonable_encoder(orders)
        orders = db.query(models.Order).order_by('id')
        
        processed_orders = []
        for order in orders:
            processed_order = {
                "id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.value,
                "pizza_size": order.pizza_size.value,
                "user_id": order.user_id
            }
            processed_orders.append(processed_order)

        return processed_orders
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not a superuser")


@order_router.get('/orders/{id}', response_model=OrderSchema)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()

    if user.is_staff:
        order = db.query(models.Order).filter(models.Order.id == id).first()
        # return jsonable_encoder(order)
        if order:
            processed_order = {
                "id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.value,
                "pizza_size": order.pizza_size.value,
                "user_id": order.user_id
            }
            return processed_order
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User noot allowed to carry out request")

from operator import attrgetter

@order_router.get('/user/orders', response_model=list[UserOrdersSchema])
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()
   
    processed_orders = []
    for order in sorted(user.orders, key=attrgetter('id'), reverse=False):
        processed_order = {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "pizza_size": order.pizza_size.value
        }
        processed_orders.append(processed_order)

    if processed_orders:
        return processed_orders

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You dont have any orders")



@order_router.get('/user/order/{order_id}', response_model=OrderSchema)
async def get_specific_order(order_id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()

    order = db.query(models.Order).filter(models.Order.user_id == user.id, models.Order.id == order_id).first()
    if order:
        processed_order = {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "pizza_size": order.pizza_size.value,
            "user_id": order.user_id
        }
        return processed_order
    # orders = user.orders
    # for order in orders:
    #     if order.id == order_id:
    #         processed_order = {
    #             "id": order.id,
    #             "quantity": order.quantity,
    #             "order_status": order.order_status.value,
    #             "pizza_size": order.pizza_size.value,
    #             "user_id": order.user_id
    #         }
    #         return processed_order
    

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No order with such id')



@order_router.put('/order/update/{order_id}', response_model=OrderSchema)
async def update_order(order_id: int, order: OrderRequest, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()

    order_to_update = db.query(models.Order).filter(models.Order.user_id == user.id, models.Order.id == order_id).first()

    if order_to_update:
        order_to_update.quantity = order.quantity
        order_to_update.pizza_size = order.pizza_size

        db.commit()
        db.refresh(order_to_update)

        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "order_status": order_to_update.order_status.value,
            "pizza_size": order_to_update.pizza_size.value,
        }

        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No order with such id')


@order_router.patch('/order/status/update/{order_id}', response_model=OrderSchema)
async def update_order_status(order_id: int, order: OrderStatusSchema, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user.is_staff:
        order_status_to_update = db.query(models.Order).filter(models.Order.id == order_id).first()
        if order_status_to_update:
            order_status_to_update.order_status = order.order_status

            db.commit()
            db.refresh(order_status_to_update)

            response = {
                "id": order_status_to_update.id,
                "quantity": order_status_to_update.quantity,
                "order_status": order_status_to_update.order_status.value,
                "pizza_size": order_status_to_update.pizza_size.value,
                "user_id": order_status_to_update.user_id
            }

            return response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not a superuser")

@order_router.delete('/order/delete/{order_id}', response_model=DeletedOrderSchema)
async def delete_an_order(order_id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = Authorize.get_jwt_subject()

    user = db.query(models.User).filter(models.User.username == current_user).first()

    order_to_delete = db.query(models.Order).filter(models.Order.id == order_id).first()

    if order_to_delete.user_id == user.id or user.is_staff:
        deleted_order_data = OrderSchema(
            id=order_to_delete.id,
            quantity=order_to_delete.quantity,
            pizza_size=order_to_delete.pizza_size.value,
            order_status=order_to_delete.order_status.value,
            user_id=order_to_delete.user.id
        )

        db.delete(order_to_delete)
        db.commit()

        response = {
            "status": "DELETED",
            "data": deleted_order_data
        }

        return response
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found your order with such id")

    
    

    
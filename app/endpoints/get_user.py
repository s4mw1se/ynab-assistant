import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/user",
    method="GET",
    response_model=UserResponse,
    responses={},
    tags=['User'],
    summary="Get user",
    description="Returns authenticated user information",
    status_code=200
)
class GetUser:
    @override
    def __call__(self) -> UserResponse:
        return UserResponse(data=UserResponseData(user=state.user))

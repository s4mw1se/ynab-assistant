import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/categories",
    method="GET",
    response_model=CategoriesResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Categories'],
    summary="Get all categories",
    description="Returns all categories grouped by category group.  Amounts (assigned, activity, available, etc.) are specific to the current plan month (UTC).",
    status_code=200
)
class GetCategories:
    @override
    def __call__(self, plan_id: str, last_knowledge_of_server: int | None = None) -> CategoriesResponse:
        return CategoriesResponse(data=CategoriesResponseData(category_groups=state.get_category_groups(plan_id), server_knowledge=100))

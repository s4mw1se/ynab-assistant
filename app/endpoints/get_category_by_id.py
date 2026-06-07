import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/categories/{category_id}",
    method="GET",
    response_model=CategoryResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Categories'],
    summary="Get a category",
    description="Returns a single category.  Amounts (assigned, activity, available, etc.) are specific to the current plan month (UTC).",
    status_code=200
)
class GetCategoryById:
    @override
    def __call__(self, plan_id: str, category_id: str) -> CategoryResponse:
        try:
            return CategoryResponse(data=CategoryResponseData(category=state.get_category(plan_id, category_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Category not found")

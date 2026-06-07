import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/months/{month}/categories/{category_id}",
    method="PATCH",
    response_model=SaveCategoryResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Categories'],
    summary="Update a category for a specific month",
    description="Update a category for a specific month.  Only `budgeted` (assigned) amount can be updated.",
    status_code=200
)
class UpdateMonthCategory:
    @override
    def __call__(self, plan_id: str, month: dt.date | str, category_id: str, body: PatchMonthCategoryWrapper) -> SaveCategoryResponse:
        try:
            updates = body.category.model_dump()
            cat = state.update_category(plan_id, category_id, updates)
            return SaveCategoryResponse(data=SaveCategoryResponseData(category=cat, server_knowledge=100))
        except KeyError:
            raise HTTPException(status_code=404, detail="Category not found")

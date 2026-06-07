import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/categories",
    method="POST",
    response_model=SaveCategoryResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Categories'],
    summary="Create a category",
    description="Creates a new category",
    status_code=201
)
class CreateCategory:
    @override
    def __call__(self, plan_id: str, body: PostCategoryWrapper) -> SaveCategoryResponse:
        import uuid
        cat = Category(
            id=f"cat_{uuid.uuid4().hex[:6]}",
            category_group_id="group_1",
            category_group_name="Immediate Obligations",
            name=body.category.name,
            hidden=False,
            internal=False,
            original_category_group_id=None,
            note=None,
            budgeted=0,
            activity=0,
            balance=0,
            deleted=False
        )
        state.create_category(plan_id, cat)
        return SaveCategoryResponse(data=SaveCategoryResponseData(category=cat, server_knowledge=100))

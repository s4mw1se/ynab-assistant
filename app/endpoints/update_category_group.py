import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/category_groups/{category_group_id}",
    method="PATCH",
    response_model=SaveCategoryGroupResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Categories'],
    summary="Update a category group",
    description="Update a category group",
    status_code=200
)
class UpdateCategoryGroup:
    @override
    def __call__(self, plan_id: str, category_group_id: str, body: PatchCategoryGroupWrapper) -> SaveCategoryGroupResponse:
        groups = state.get_category_groups(plan_id)
        for g in groups:
            if g.id == category_group_id:
                if body.category_group.name:
                    g.name = body.category_group.name
                return SaveCategoryGroupResponse(data=SaveCategoryGroupResponseData(category_group=g, server_knowledge=100))
        raise HTTPException(status_code=404, detail="Category group not found")

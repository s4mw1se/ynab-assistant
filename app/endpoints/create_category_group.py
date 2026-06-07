import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/category_groups",
    method="POST",
    response_model=SaveCategoryGroupResponse,
    responses={400: {'model': 'ErrorResponse'}},
    tags=['Categories'],
    summary="Create a category group",
    description="Creates a new category group",
    status_code=201
)
class CreateCategoryGroup:
    @override
    def __call__(self, plan_id: str, body: PostCategoryGroupWrapper) -> SaveCategoryGroupResponse:
        import uuid
        group = CategoryGroupWithCategories(
            id=f"group_{uuid.uuid4().hex[:6]}",
            name=body.category_group.name,
            hidden=False,
            internal=False,
            deleted=False,
            categories=[]
        )
        state.category_groups.setdefault(plan_id, []).append(group)
        return SaveCategoryGroupResponse(data=SaveCategoryGroupResponseData(category_group=group, server_knowledge=100))

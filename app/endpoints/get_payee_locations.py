import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payee_locations",
    method="GET",
    response_model=PayeeLocationsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Payee Locations'],
    summary="Get all payee locations",
    description="Returns all payee locations",
    status_code=200
)
class GetPayeeLocations:
    @override
    def __call__(self, plan_id: str) -> PayeeLocationsResponse:
        return PayeeLocationsResponse(data=PayeeLocationsResponseData(payee_locations=state.get_payee_locations(plan_id), server_knowledge=100))

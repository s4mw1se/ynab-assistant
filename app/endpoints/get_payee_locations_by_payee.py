import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payees/{payee_id}/payee_locations",
    method="GET",
    response_model=PayeeLocationsResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Payee Locations'],
    summary="Get all locations for a payee",
    description="Returns all payee locations for a specified payee",
    status_code=200
)
class GetPayeeLocationsByPayee:
    @override
    def __call__(self, plan_id: str, payee_id: str) -> PayeeLocationsResponse:
        return PayeeLocationsResponse(data=PayeeLocationsResponseData(payee_locations=state.get_payee_locations(plan_id), server_knowledge=100))

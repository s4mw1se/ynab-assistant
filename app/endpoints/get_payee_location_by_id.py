import datetime as dt
from typing import override, Literal
from fastapi import Depends, HTTPException
from app.core.decorators import endpoint
from app.core.state import state
from app.schemas import *

@endpoint(
    path="/plans/{plan_id}/payee_locations/{payee_location_id}",
    method="GET",
    response_model=PayeeLocationResponse,
    responses={404: {'model': 'ErrorResponse'}},
    tags=['Payee Locations'],
    summary="Get a payee location",
    description="Returns a single payee location",
    status_code=200
)
class GetPayeeLocationById:
    @override
    def __call__(self, plan_id: str, payee_location_id: str) -> PayeeLocationResponse:
        try:
            return PayeeLocationResponse(data=PayeeLocationResponseData(payee_location=state.get_payee_location(plan_id, payee_location_id)))
        except KeyError:
            raise HTTPException(status_code=404, detail="Payee Location not found")

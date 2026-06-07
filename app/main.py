from fastapi import FastAPI
from app.core.decorators import registry
import app.endpoints  # Load all endpoints to register them

app = FastAPI(
    title="YNAB API Mock Server",
    description="A complete mock implementation of the YNAB API spec",
    version="1.85.0"
)

# Register all routes from decorator registry
for ep in registry.endpoints:
    cls = ep["cls"]
    # Instantiate class to use as route callable
    handler = cls()
    app.add_api_route(
        path=f"/v1{ep['path']}",
        endpoint=handler,
        methods=[ep["method"]],
        response_model=ep["response_model"],
        responses=ep["responses"],
        tags=ep["tags"],
        summary=ep["summary"],
        description=ep["description"],
        status_code=ep["status_code"]
    )

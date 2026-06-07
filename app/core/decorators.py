from typing import Type, Any, List, Dict, Optional
from fastapi import APIRouter

class EndpointRegistry:
    def __init__(self):
        self.endpoints = []

    def register(
        self,
        path: str,
        method: str,
        response_model: Any = None,
        responses: Optional[Dict[int, Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: int = 200,
    ):
        def decorator(cls: Type):
            self.endpoints.append({
                "cls": cls,
                "path": path,
                "method": method.upper(),
                "response_model": response_model,
                "responses": responses,
                "tags": tags,
                "summary": summary,
                "description": description,
                "status_code": status_code,
            })
            return cls
        return decorator

registry = EndpointRegistry()
endpoint = registry.register

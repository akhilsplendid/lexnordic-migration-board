from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.permits.catalog import PERMIT_ROUTES, ROUTES_BY_ID, route_families, serialize_route
from app.permits.readiness import match_routes


router = APIRouter(prefix="/permits", tags=["permits"])


class PermitMatchRequest(BaseModel):
    query: str | None = Field(default=None, description="Natural-language user goal.")
    route_id: str | None = Field(default=None, description="Explicit route id, if known.")
    facts: dict[str, Any] = Field(default_factory=dict)
    documents: list[str] = Field(default_factory=list)
    limit: int = Field(default=8, ge=1, le=20)


@router.get("/routes")
def list_permit_routes(family: str | None = Query(default=None)) -> dict[str, Any]:
    routes = [route for route in PERMIT_ROUTES if family is None or route.family == family]
    return {
        "count": len(routes),
        "families": route_families(),
        "routes": [serialize_route(route) for route in routes],
    }


@router.get("/routes/{route_id}")
def get_permit_route(route_id: str) -> dict[str, Any]:
    route = ROUTES_BY_ID.get(route_id)
    if route is None:
        raise HTTPException(status_code=404, detail=f"Unknown permit route: {route_id}")
    return serialize_route(route)


@router.post("/match")
def match_permit_routes(request: PermitMatchRequest) -> dict[str, Any]:
    if request.route_id and request.route_id not in ROUTES_BY_ID:
        raise HTTPException(status_code=404, detail=f"Unknown permit route: {request.route_id}")
    results = match_routes(
        query=request.query,
        route_id=request.route_id,
        facts=request.facts,
        documents=request.documents,
        limit=request.limit,
    )
    return {
        "query": request.query,
        "route_id": request.route_id,
        "results": results,
    }

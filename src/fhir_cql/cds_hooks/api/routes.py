"""CDS Hooks API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request

from ..models.discovery import DiscoveryResponse
from ..models.feedback import FeedbackRequest
from ..models.request import CDSRequest
from ..models.response import CDSResponse
from ..service.card_builder import CardBuilder
from ..service.executor import CDSExecutor
from ..service.registry import ServiceRegistry


def get_registry(request: Request) -> ServiceRegistry:
    """Get service registry from app state."""
    return request.app.state.registry


def get_executor(request: Request) -> CDSExecutor:
    """Get CQL executor from app state."""
    return request.app.state.executor


def get_card_builder(request: Request) -> CardBuilder:
    """Get card builder from app state."""
    return request.app.state.card_builder


def create_router() -> APIRouter:
    """Create the CDS Hooks API router."""

    router = APIRouter(tags=["CDS Hooks"])

    @router.get(
        "",
        response_model=DiscoveryResponse,
        summary="Discover CDS Services",
        description="Returns the list of available CDS Services",
    )
    async def discovery(
        registry: ServiceRegistry = Depends(get_registry),
    ) -> DiscoveryResponse:
        """CDS Hooks Discovery endpoint.

        See: https://cds-hooks.hl7.org/2.0/#discovery
        """
        return registry.get_discovery_response()

    @router.post(
        "/{service_id}",
        response_model=CDSResponse,
        summary="Invoke CDS Service",
        description="Execute CDS logic and return decision support cards",
    )
    async def invoke_service(
        service_id: str,
        request: CDSRequest,
        registry: ServiceRegistry = Depends(get_registry),
        executor: CDSExecutor = Depends(get_executor),
        card_builder: CardBuilder = Depends(get_card_builder),
    ) -> CDSResponse:
        """CDS Service invocation endpoint.

        See: https://cds-hooks.hl7.org/2.0/#calling-a-cds-service
        """
        # Get service configuration
        service = registry.get_service(service_id)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"CDS Service not found: {service_id}",
            )

        # Validate hook matches
        if request.hook != service.hook:
            raise HTTPException(
                status_code=400,
                detail=f"Hook mismatch: expected {service.hook}, got {request.hook}",
            )

        try:
            # Execute CQL logic
            results = executor.execute(service, request)

            # Build response cards
            response = card_builder.build_response(service, results)

            return response

        except Exception:
            # Per CDS Hooks spec, return empty cards on error
            # In production, you'd want to log the error
            return CDSResponse(cards=[])

    @router.post(
        "/{service_id}/feedback",
        status_code=200,
        summary="Submit Feedback",
        description="Submit feedback on CDS cards",
    )
    async def submit_feedback(
        service_id: str,
        feedback_request: FeedbackRequest,
        registry: ServiceRegistry = Depends(get_registry),
    ) -> dict[str, str]:
        """CDS Hooks Feedback endpoint.

        See: https://cds-hooks.hl7.org/2.0/#feedback
        """
        service = registry.get_service(service_id)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"CDS Service not found: {service_id}",
            )

        # In a real implementation, you would store the feedback
        # For now, just acknowledge receipt
        return {"status": "accepted", "count": str(len(feedback_request.feedback))}

    return router

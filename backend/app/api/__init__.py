from .incidents import router as incidents_router
from .dashboard import router as dashboard_router

__all__ = ["incidents_router", "dashboard_router"]

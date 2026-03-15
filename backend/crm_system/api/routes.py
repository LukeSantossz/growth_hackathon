from fastapi import APIRouter
from api.endpoints import auth, clients, health, client_bases, onboarding

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(client_bases.router, prefix="/bases", tags=["bases"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])

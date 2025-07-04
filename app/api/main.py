from fastapi import APIRouter

from app.api.routes import items, layers, login, users, utils, ai

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(layers.router, prefix="/layers", tags=["layers"])
api_router.include_router(ai.router, prefix="/AI", tags=["AI"])

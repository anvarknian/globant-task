from fastapi import FastAPI

from app.api.router import api_router
from app.prisma_config import prisma_client


def create_app() -> FastAPI:
    fastapi = FastAPI(title="GLOBANT", version="0.1.0", debug=False)
    fastapi.include_router(api_router, prefix="/api")

    @fastapi.on_event('startup')
    async def startup():
        await prisma_client.connect()

    @fastapi.on_event('shutdown')
    async def shutdown():
        await prisma_client.disconnect()

    return fastapi


app = create_app()

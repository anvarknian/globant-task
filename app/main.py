from fastapi import FastAPI
from prisma import Prisma

from app.api.router import api_router

app = FastAPI(title="GLOBANT", version="0.1.0", debug=False)

prisma = Prisma(auto_register=True, connect_timeout=600)

app.include_router(api_router, prefix="/api")


@app.on_event('startup')
async def startup() -> None:
    await prisma.connect()


@app.on_event('shutdown')
async def shutdown() -> None:
    if prisma.is_connected():
        await prisma.disconnect()

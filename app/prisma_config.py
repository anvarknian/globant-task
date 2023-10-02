import logging

from prisma import Prisma


class PrismaManager:
    def __init__(self):
        logging.getLogger('prisma').setLevel(logging.ERROR)
        self.prisma = Prisma(auto_register=True)

    async def connect(self):
        await self.prisma.connect()

    async def disconnect(self):
        if self.prisma.is_connected():
            await self.prisma.disconnect()


prisma_client = PrismaManager()

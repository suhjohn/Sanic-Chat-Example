import aioredis

from chat_example import config


class RedisConnection:
    def __init__(self):
        self._pool = None
        self._connections = {}

    async def get_redis(self):
        if not self._pool:
            print("connecting again")
            await self.connect()
        return self._pool

    async def connect(self):
        self._pool = await aioredis.create_pool(
            config.REDIS_HOSTNAME,
            minsize=5, maxsize=10
        )

    async def close(self):
        self._pool.close()
        await self._pool.wait_closed()


redis_conn_pub = RedisConnection()
redis_conn_sub = RedisConnection()

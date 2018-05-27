from aioredis import ConnectionsPool, Channel, RedisConnection
from websockets import WebSocketCommonProtocol

from .redis import redis_conn_pub, redis_conn_sub


class Room:
    def __init__(self, channel_name):
        self._pub: ConnectionsPool = None
        self._sub: ConnectionsPool = None
        self._channel = Channel(channel_name, is_pattern=False)

    @classmethod
    async def initialize(cls, channel_name):
        room = cls(channel_name=channel_name)
        sub = await redis_conn_sub.get_redis()
        room._sub = sub
        pub = await redis_conn_pub.get_redis()
        room._pub = pub
        return room

    async def join_room(self):
        conn: RedisConnection
        with await self._sub as conn:
            await conn.execute_pubsub("subscribe", self._channel)

    async def leave_room(self):
        conn: RedisConnection
        with await self._sub as conn:
            await conn.execute_pubsub("unsubscribe", self._channel)

    async def send_msg(self, websocket: WebSocketCommonProtocol):
        message = await self._channel.get()
        await websocket.send(message)

    async def pub_msg(self, websocket: WebSocketCommonProtocol):
        with await self._pub as conn:
            message = await websocket.recv()
            await conn.execute("publish", "room", message)
            print(message)

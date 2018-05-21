import websockets
from aioredis import ConnectionsPool, Channel, RedisConnection
from sanic.log import logger

from .redis import redis_conn_pub, redis_conn_sub


class Room:
    def __init__(self):
        self._pub: ConnectionsPool = None
        self._sub: ConnectionsPool = None

    @classmethod
    async def initialize(cls):
        room = cls()
        pub = await redis_conn_pub.get_redis()
        room._pub = pub
        sub = await redis_conn_sub.get_redis()
        room._sub = sub
        return room

    async def producer_handler(self, websocket, path=""):
        """

        :param websocket:
        :param path:
        :return:
        """
        conn: RedisConnection
        with await self._sub as conn:
            channel = Channel('room'.format(path), is_pattern=False)
            await conn.execute_pubsub('subscribe', channel)
            try:
                while True:
                    print('waiting')
                    message = await channel.get(encoding="utf-8")
                    print(f"Waited: {message}")
                    await websocket.send(message)
                    print("sent")
            except websockets.ConnectionClosed:
                print(f"connection is closed: {conn.closed}")

    async def consumer_handler(self, websocket: websockets.WebSocketServerProtocol, path=""):
        """
        websocket listens to incoming traffic and then pipes in the processed data to a "consumer" co-routine,
        in this example a call to Redis's PUBLISH function.

        :param websocket:
        :param path:
        :return:
        """
        conn: RedisConnection
        with await self._pub as conn:
            try:
                while True:
                    # Receive data from "the outside world"
                    print("Receiving")
                    message = await websocket.recv()
                    print(f"Received: {message}")
                    # Feed this data to the PUBLISH co-routine
                    await conn.execute("publish", "room", message)
                    print("published")
            except websockets.ConnectionClosed:
                logger.info(f"User {websocket.remote_address} Left")

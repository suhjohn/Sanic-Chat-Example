import asyncio
import ujson

import websockets
from aioredis import ConnectionsPool, Channel, RedisConnection
from sanic.log import logger
from websockets import WebSocketCommonProtocol

from .redis import redis_conn_pub, redis_conn_sub


class ProducerHandler:
    def __init__(self):
        self.redis = None
        self.channel = None

    @classmethod
    async def initialize(cls, channel):
        handler = cls()
        redis = await redis_conn_sub.get_redis()
        handler.redis = redis
        handler.channel = channel
        return handler

    async def broadcast(self, websocket: WebSocketCommonProtocol):
        conn: RedisConnection
        with await self.redis as conn:
            await conn.execute_pubsub('subscribe', self.channel)
            try:
                while True:
                    message = await self.channel.get(encoding="utf-8")
                    await websocket.send(message)
            except websockets.ConnectionClosed as e:
                print(f"<ProducerHandler:broadcast>[error] {e}")


class ConsumerHandler:
    def __init__(self):
        self._pub: ConnectionsPool = None
        self._channel: Channel = None

    @classmethod
    async def initialize(cls, channel):
        room = cls()
        pub = await redis_conn_pub.get_redis()
        room._pub = pub
        room._channel = channel
        return room

    async def handle(self, websocket: websockets.WebSocketCommonProtocol):
        """
        websocket listens to incoming traffic and then pipes in the processed data to a "consumer" co-routine,
        in this example a call to Redis's PUBLISH function.
        msg format: {
            "action_type": <action_type>,
            "data": <data>
        }

        :param websocket:
        :param path:
        :return:
        """

        try:
            while True:
                msg = await websocket.recv()
                # TODO Validate message is of the correct format
                loaded_msg = ujson.loads(msg)
                action_type = loaded_msg.get("action_type")
                try:
                    func = getattr(self, f"_{action_type}")
                    if not asyncio.iscoroutinefunction(func):
                        raise AttributeError
                    await func(loaded_msg)
                except AttributeError:
                    logger.warn(f"Invalid action requested: {action_type} full msg: {msg}")

        except websockets.ConnectionClosed as e:
            print(f"<ConsumerHandler:handle>[error] {e}")

    async def _chat(self, msg):
        dumped_msg = ujson.dumps(msg)
        conn: RedisConnection
        with await self._pub as conn:
            await conn.execute("publish", self._channel.name, dumped_msg)


async def chat(request, websocket: WebSocketCommonProtocol):
    # TODO Validate first message from websocket is the channel name
    channel_name = await websocket.recv()
    channel_name = ujson.loads(channel_name)

    channel = Channel(channel_name, is_pattern=False)
    consumer_handler = await ConsumerHandler.initialize(channel)
    producer_handler = await ProducerHandler.initialize(channel)

    consumer_task = asyncio.ensure_future(consumer_handler.handle(websocket))
    producer_task = asyncio.ensure_future(producer_handler.broadcast(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

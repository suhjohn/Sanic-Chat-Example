import asyncio

from sanic.response import file
from websockets import WebSocketCommonProtocol

from chat_example.room import Room


async def index(request):
    return await file('static/index.html')


async def chat(request, websocket: WebSocketCommonProtocol):
    room = await Room.initialize()
    consumer_task = asyncio.ensure_future(room.consumer_handler(websocket))
    producer_task = asyncio.ensure_future(room.producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,

    )

    for task in pending:
        task.cancel()

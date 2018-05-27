import asyncio

import websockets
from sanic.response import file
from websockets import WebSocketCommonProtocol

from backend.room import Room


async def index(request):
    return await file('static/index.html')


async def chat(request, websocket: WebSocketCommonProtocol):
    channel_name = await websocket.recv()
    room = await Room.initialize(channel_name)
    await room.join_room()
    print(f"joined room {room} with name {channel_name}")
    try:
        while True:
            await room.pub_msg(websocket)


    except websockets.ConnectionClosed:
        print("connection is closed!")

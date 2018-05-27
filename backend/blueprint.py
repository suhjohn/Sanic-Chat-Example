from sanic import Blueprint

from .websockets import chat

bp = Blueprint(__name__.split('.')[0], url_prefix='/')

bp.add_websocket_route(handler=chat, uri="chat")

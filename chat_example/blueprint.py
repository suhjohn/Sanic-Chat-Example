from sanic import Blueprint

from chat_example.views import chat, index

bp = Blueprint(__name__.split('.')[0], url_prefix='/')

bp.add_route(handler=index, uri="")
bp.add_websocket_route(handler=chat, uri="chat")

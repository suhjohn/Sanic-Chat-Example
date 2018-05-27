from sanic import Sanic

from .redis import redis_conn_pub, redis_conn_sub

app = Sanic(__name__)

from .blueprint import bp

app.blueprint(bp)


@app.listener('before_server_start')
async def start_redis(app, loop):
    await redis_conn_pub.connect()
    await redis_conn_sub.connect()


@app.listener('before_server_start')
async def start_db(app, loop):
    pass


@app.listener('after_server_stop')
async def end_redis(app, loop):
    await redis_conn_pub.close()
    await redis_conn_sub.close()


@app.listener('after_server_stop')
async def end_db(app, loop):
    pass

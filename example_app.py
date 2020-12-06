#!/usr/bin/env python3

from aiohttp import web


async def handle(_: web.Request):
    return web.Response(text="Hello Earthling, I hope you are authenticated.")


app = web.Application()
app.add_routes([web.get("/", handle)])

if __name__ == "__main__":
    web.run_app(app, port=9001)

import asyncio

from haproxyspoa.spoa_server import SpoaServer

if __name__ == "__main__":
    print("Trying to run server")
    server = SpoaServer()
    asyncio.run(server.run(), debug=True)
    print("The server is done")
import time

import uvicorn
from fastapi import Response, FastAPI
from crypto_plus import CryptoPlus
from starlette.responses import StreamingResponse
from fastapi import WebSocket

app = FastAPI()

rsa = CryptoPlus.load()
server_uid = "nasller"
subject_name = f"{server_uid}.lsrv.jetbrains.com"
cert = rsa.dumps_cert(
    subject_name=subject_name, issuer_name="JetProfile CA", format="DER"
)


class XMLResponse(Response):
    media_type = "application/xml"


@app.websocket("/ws")
async def web_socket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data * 2)


def stream():
    # async def stream():
    for i in range(10):
        yield f"{str(i)}\n".encode()
        time.sleep(0.5)
        # await asyncio.sleep(1)
        i += 1


@app.get("/")
def event_stream():
    # async def root():
    return StreamingResponse(stream(), media_type="text/event-stream")
    # return StreamingResponse(stream())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)

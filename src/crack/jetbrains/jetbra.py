import base64
import time

import uvicorn
from fastapi import Response, FastAPI
from crypto_plus import CryptoPlus
from starlette.responses import StreamingResponse
from fastapi import WebSocket

app = FastAPI()

rsa = CryptoPlus.load()


class XMLResponse(Response):
    media_type = 'application/xml'


@app.websocket("/ws")
async def web_socket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data * 2)


def stream():
    # async def stream():
    for i in range(10):
        yield f'{str(i)}\n'.encode()
        time.sleep(0.5)
        # await asyncio.sleep(1)
        i += 1


@app.get('/')
def event_stream():
    # async def root():
    return StreamingResponse(stream(), media_type="text/event-stream")
    # return StreamingResponse(stream())


@app.post('/')
async def root():
    xml_content = '<ObtainTicketResponse><action>NONE</action><confirmationStamp></confirmationStamp><leaseSignature>16b52e7ac379409f066cec752ade86c51bbd3241d434361dd887c0c7a9e599e15810a510a62abfbb4748bdfcb9b9c16d07ae1600b825c815b3d70b90f9016096</leaseSignature><message>Salt not specified</message><prolongationPeriod>0</prolongationPeriod><responseCode>ERROR</responseCode><salt>0</salt><serverLease>1712035470621:7u5bpyjjag</serverLease><serverUid>7u5bpyjjag</serverUid><validationDeadlinePeriod>-1</validationDeadlinePeriod><validationPeriod>0</validationPeriod></ObtainTicketResponse>'
    xml_signature = rsa.sign(xml_content.encode(), 'SHA1')
    xml = f'<!--  SHA1withRSA-{base64.b64encode(xml_signature).decode()}  -->\n{xml_content}'
    return XMLResponse(xml)


@app.get('/rpc/ping.action')
async def ping(salt=''):
    # xml_content = f'<PingResponse><action>NONE</action><confirmationStamp></confirmationStamp><leaseSignature>16b52e7ac379409f066cec752ade86c51bbd3241d434361dd887c0c7a9e599e15810a510a62abfbb4748bdfcb9b9c16d07ae1600b825c815b3d70b90f9016096</leaseSignature><message></message><responseCode>OK</responseCode><salt>{salt}</salt><serverLease>1712035470621:7u5bpyjjag</serverLease><serverUid>7u5bpyjjag</serverUid><validationDeadlinePeriod>-1</validationDeadlinePeriod><validationPeriod>3722216</validationPeriod></PingResponse>'
    xml_content = f'<PingResponse><message></message><responseCode>OK</responseCode><salt>{salt}</salt></PingResponse>'
    xml_signature = rsa.sign(xml_content.encode(), 'SHA1')
    xml = f'<!--  SHA1withRSA-{base64.b64encode(xml_signature).decode()}  -->\n{xml_content}'
    return XMLResponse(xml)


@app.get('/rpc/obtainTicket.action')
async def obtain_ticket(salt="", username=""):
    prolongation_period = "607875500"
    xml_content = f"<ObtainTicketResponse><message></message><prolongationPeriod>{prolongation_period}</prolongationPeriod><responseCode>OK</responseCode><salt>{salt}</salt><ticketId>1</ticketId><ticketProperties>licensee={username}licenseType=0</ticketProperties></ObtainTicketResponse>"
    xml_signature = rsa.sign(xml_content.encode(), 'MD5').hex()
    xml = f'<!-- {xml_signature} -->{xml_content}'
    return XMLResponse(xml)


@app.get('/rpc/releaseTicket.action')
async def release_ticket(salt=""):
    xml_content = f'<ReleaseTicketResponse><message></message><responseCode>OK</responseCode><salt>{salt}</salt></ReleaseTicketResponse>'
    xml_signature = rsa.sign(xml_content.encode(), 'MD5').hex()
    xml = f'<!-- {xml_signature} -->{xml_content}'
    return XMLResponse(xml)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)

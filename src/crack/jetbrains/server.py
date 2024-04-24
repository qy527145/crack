import base64
import os
import random
import time
from base64 import b64encode

import uvicorn
from crypto_plus import CryptoPlus
from fastapi import Response, FastAPI
from starlette.responses import PlainTextResponse

from jetbrains import JetbrainsKeyGen
from plugins import JetBrainPlugin

server_uid = os.environ.get('NAME', 'crack')
subject_name = f'{server_uid}.lsrv.jetbrains.com'
server_uid_camel = server_uid.upper()[:1] + server_uid[1:]

# 首次启动更新插件信息
JetBrainPlugin().update().make_licenses()


def ensure_key():
    if not os.path.exists("ls.pem"):
        rsa2 = CryptoPlus.generate_rsa()
        rsa2.dump(key_path='ls.pem', pub_key_path='ls_pub.pem')
        rsa2.dump_cert(subject_name=subject_name, issuer_name='License Servers CA', cert_path='ls_cert.crt')
    else:
        rsa2 = CryptoPlus.load(key_path='ls.pem')
        ls_cert = CryptoPlus.load(key_path='ls_cert.crt')
        if f'CN={subject_name}' != ls_cert.key.subject.rfc4514_string():
            rsa2.dump_cert(subject_name=subject_name, issuer_name='License Servers CA', cert_path='ls_cert.crt')

    if not os.path.isfile('key.pem'):
        rsa2 = CryptoPlus.generate_rsa()
        rsa2.dump()
        rsa2.dump_cert(subject_name=server_uid_camel, issuer_name='JetProfile CA')


ensure_key()
rsa1 = CryptoPlus.load('ls.pem')
rsa2 = CryptoPlus.load()

cert1 = "".join(open('ls_cert.crt').read().split(chr(10))[1:-2])
arg1 = int.from_bytes(CryptoPlus.loads(cert1).key.signature, 'big')
mod1 = 657823416415964932845156435107145357714205418747915356734397055242964933221752404166614935255105249101653916721681603662754307632457128805443068644284748929421507178622933348669378235847742899773920765918770105482851534467296284105250512573151705220224379509383835022323282176179690146311979451556541118129344282127375534752754929526193258755897888515754328964698687671896985405008425332766082319260988023654359845072776189451448786758245414253386146246727354454047135428416624852422567360097346671648093064429279847823280592246506886401865455491924420415707803245018138595108029359998829520236522620749918729938206134739331246902031807601266419258080411903201595710155467901291142142443220333539750397923736434950558371997170985472272249812750161962720036837656464089126216749585148030883029438285184930024286517865710539947589764564204842426698322404033441531662829238875205420761652375337327297032255730262635511533223504109798364923988127319356119135982652788834405038113746394301957551167740345788175766290794604666781402329824924118191746319728033878045396093674696713022814027690165596773992550010915823534552020920573926469894452526033833249442230929742486602298477270672101197444729222659891038350303699501280729658274069437

cert2 = "".join(open('cert.crt').read().split(chr(10))[1:-2])
arg2 = int.from_bytes(CryptoPlus.loads(cert2).key.signature, 'big')
mod2 = 860106576952879101192782278876319243486072481962999610484027161162448933268423045647258145695082284265933019120714643752088997312766689988016808929265129401027490891810902278465065056686129972085119605237470899952751915070244375173428976413406363879128531449407795115913715863867259163957682164040613505040314747660800424242248055421184038777878268502955477482203711835548014501087778959157112423823275878824729132393281517778742463067583320091009916141454657614089600126948087954465055321987012989937065785013284988096504657892738536613208311013047138019418152103262155848541574327484510025594166239784429845180875774012229784878903603491426732347994359380330103328705981064044872334790365894924494923595382470094461546336020961505275530597716457288511366082299255537762891238136381924520749228412559219346777184174219999640906007205260040707839706131662149325151230558316068068139406816080119906833578907759960298749494098180107991752250725928647349597506532778539709852254478061194098069801549845163358315116260915270480057699929968468068015735162890213859113563672040630687357054902747438421559817252127187138838514773245413540030800888215961904267348727206110582505606182944023582459006406137831940959195566364811905585377246353

patch = f'; license server\nEQUAL,{arg1},65537,{mod1}->{pow(arg1, 65537, rsa1.public_key.n)}\n; Jetbrains IDEs & Plugins Activation Code\nEQUAL,{arg2},65537,{mod2}->{pow(arg2, 65537, rsa2.public_key.n)}'


class XMLResponse(Response):
    media_type = 'application/xml'


app = FastAPI()


@app.get('/rpc/ping.action')
async def ping(salt, machineId):
    confirmation_stamp = f'{int(1000 * time.time())}:{machineId}'
    server_lease = f'4102415999000:{server_uid}'
    xml_content = f'''<PingResponse><action>NONE</action><confirmationStamp>{confirmation_stamp}:SHA1withRSA:{b64encode(rsa1.sign(confirmation_stamp.encode(), 'SHA1')).decode()}:{cert1}</confirmationStamp><leaseSignature>SHA512withRSA-{b64encode(rsa2.sign(server_lease.encode(), 'SHA512')).decode()}-{cert2}</leaseSignature><message></message><responseCode>OK</responseCode><salt>{salt}</salt><serverLease>{server_lease}</serverLease><serverUid>{server_uid}</serverUid><validationDeadlinePeriod>-1</validationDeadlinePeriod><validationPeriod>600000</validationPeriod></PingResponse>'''
    xml = f'<!-- SHA1withRSA-{base64.b64encode(rsa1.sign(xml_content.encode(), 'SHA1')).decode()}-{cert1} -->\n{xml_content}'
    return XMLResponse(xml)


@app.get('/rpc/obtainTicket.action')
async def obtain_ticket(salt, machineId, userName):
    confirmation_stamp = f'{int(1000 * time.time())}:{machineId}'
    server_lease = f'4102415999000:{server_uid}'
    xml_content = f'''<ObtainTicketResponse><action>NONE</action><confirmationStamp>{confirmation_stamp}:SHA1withRSA:{b64encode(rsa1.sign(confirmation_stamp.encode(), 'SHA1')).decode()}:{cert1}</confirmationStamp><leaseSignature>SHA512withRSA-{b64encode(rsa2.sign(server_lease.encode(), 'SHA512')).decode()}-{cert2}</leaseSignature><message></message><prolongationPeriod>600000</prolongationPeriod><responseCode>OK</responseCode><salt>{salt}</salt><serverLease>{server_lease}</serverLease><serverUid>{server_uid}</serverUid><ticketId>{random.randbytes(5).hex()}</ticketId><ticketProperties>licensee={userName}\tlicenseType=4\tmetadata=0120211231PSAN000005</ticketProperties><validationDeadlinePeriod>-1</validationDeadlinePeriod><validationPeriod>600000</validationPeriod></ObtainTicketResponse>'''
    xml = f'<!-- SHA1withRSA-{base64.b64encode(rsa1.sign(xml_content.encode(), 'SHA1')).decode()}-{cert1} -->\n{xml_content}'
    return XMLResponse(xml)


@app.get('/rpc/releaseTicket.action')
async def release_ticket(salt="", machineId=""):
    confirmation_stamp = f'{int(1000 * time.time())}:{machineId}'
    server_lease = f'4102415999000:{server_uid}'
    xml_content = f'''<ReleaseTicketRpcService><action>NONE</action><confirmationStamp>{confirmation_stamp}:SHA1withRSA:{b64encode(rsa1.sign(confirmation_stamp.encode(), 'SHA1')).decode()}:{cert1}</confirmationStamp><leaseSignature>SHA512withRSA-{b64encode(rsa2.sign(server_lease.encode(), 'SHA512')).decode()}-{cert2}</leaseSignature><message></message><responseCode>OK</responseCode><salt>{salt}</salt><serverLease>{server_lease}</serverLease><serverUid>{server_uid}</serverUid><validationDeadlinePeriod>-1</validationDeadlinePeriod><validationPeriod>600000</validationPeriod></ReleaseTicketRpcService>'''
    xml = f'<!-- SHA1withRSA-{base64.b64encode(rsa1.sign(xml_content.encode(), 'SHA1')).decode()}-{cert1} -->\n{xml_content}'
    print(xml)
    return XMLResponse(xml)


@app.get('/')
async def power():
    return PlainTextResponse(patch)


@app.get('/code')
async def code(license_id=None, license_name=None):
    return PlainTextResponse(JetbrainsKeyGen().generate(license_id, license_name))


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)

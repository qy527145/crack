import json
from base64 import b64encode, b64decode

from crypto_plus import CryptoPlus

from crack.base import KeyGen

# power[Result] 模板
power_result_template = 'EQUAL,{arg},65537,860106576952879101192782278876319243486072481962999610484027161162448933268423045647258145695082284265933019120714643752088997312766689988016808929265129401027490891810902278465065056686129972085119605237470899952751915070244375173428976413406363879128531449407795115913715863867259163957682164040613505040314747660800424242248055421184038777878268502955477482203711835548014501087778959157112423823275878824729132393281517778742463067583320091009916141454657614089600126948087954465055321987012989937065785013284988096504657892738536613208311013047138019418152103262155848541574327484510025594166239784429845180875774012229784878903603491426732347994359380330103328705981064044872334790365894924494923595382470094461546336020961505275530597716457288511366082299255537762891238136381924520749228412559219346777184174219999640906007205260040707839706131662149325151230558316068068139406816080119906833578907759960298749494098180107991752250725928647349597506532778539709852254478061194098069801549845163358315116260915270480057699929968468068015735162890213859113563672040630687357054902747438421559817252127187138838514773245413540030800888215961904267348727206110582505606182944023582459006406137831940959195566364811905585377246353->{result}'


class JetbrainsKeyGen(KeyGen):

    def __init__(self):
        try:
            obj = CryptoPlus.load()
        except Exception:
            obj = CryptoPlus.generate_rsa()
            obj.dump()
            obj.dump_cert(subject_name='Crack', issuer_name='JetProfile CA')
        self.crypto_plus = obj
        self.certificate_text = open('cert.crt').read()
        self.certificate = CryptoPlus.loads(self.certificate_text).raw_private_key
        self.license_data = json.load(open('licenses.json'))

    def generate(self):
        cert = "".join(self.certificate_text.split(chr(10))[1:-2])
        # 激活码组成
        license_id = self.license_data['licenseId']
        license_info = json.dumps(self.license_data, separators=(',', ':'))
        signature = self.crypto_plus.sign(license_info.encode(), "SHA1")
        activation_code = (
            f'{license_id}-'
            f'{b64encode(license_info.encode()).decode()}'
            f'-{b64encode(signature).decode()}-'
            f'{cert}'
        )
        return activation_code

    def parse(self, licenses):
        license_id, license_info, signature, cert = licenses.split('-')
        license_info = b64decode(license_info)
        signature = b64decode(signature)
        cert = f"-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----\n"
        certificate = CryptoPlus.loads(cert)
        assert certificate.verify(license_info, signature, "SHA1")
        license_info = json.loads(license_info.decode())
        assert license_id == license_info['licenseId']
        return license_info

    def patch(self):
        arg = int.from_bytes(self.certificate.signature, 'big')
        result = pow(arg, 65537, self.crypto_plus.public_key.n)
        return power_result_template.format(arg=arg, result=result)


if __name__ == '__main__':
    from plugins import JetBrainPlugin

    JetBrainPlugin().update().make_licenses()
    JetbrainsKeyGen().run()

import base64
import json
import os

from Crypto.Cipher import AES
from crypto_plus import CryptoPlus

from crack.base import KeyGen

template_license_data = {
    "version": 1,
    "licensee": {"Name": "null", "Company": "null", "Email": "null@null.com"},
    "issued_at": "2023-01-01",
    "expires_at": "2100-12-31",
    "notify_admins_at": "2100-12-01",
    "notify_users_at": "2100-12-01",
    "block_changes_at": "2100-12-10",
    "cloud_licensing_enabled": False,
    "offline_cloud_licensing_enabled": False,
    "auto_renew_enabled": False,
    "seat_reconciliation_enabled": False,
    "operational_metrics_enabled": False,
    "generated_from_customers_dot": False,
    "restrictions": {"active_user_count": 99999, "plan": "ultimate"},
}


class GitlabKeyGen(KeyGen):
    def __init__(self):
        self.license_data = template_license_data
        try:
            rsa = CryptoPlus.load()
        except Exception:  # noqa
            rsa = CryptoPlus.generate_rsa(2048)
            rsa.dump(pub_key_path=".license_encryption_key.pub")
        self.crypto_plus = rsa

    def generate(self):
        aes_key = os.urandom(16)
        aes_iv = os.urandom(16)
        license_plaintext = json.dumps(self.license_data).encode()
        if len(license_plaintext) % 16 > 0:
            pad = 16 - len(license_plaintext) % 16
            license_plaintext = license_plaintext + pad.to_bytes(1) * pad
        encrypt_data = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(
            license_plaintext
        )
        # 原则上不应该使用私钥加密，尽管CryptoPlus支持私钥加密
        encrypt_key = self.crypto_plus.encrypt_by_private_key(aes_key)
        encrypt_license = {
            "data": base64.b64encode(encrypt_data).decode(),
            "key": base64.b64encode(encrypt_key).decode(),
            "iv": base64.b64encode(aes_iv).decode(),
        }
        encrypt_license = json.dumps(encrypt_license).encode()
        encrypt_license = base64.b64encode(encrypt_license)
        with open("GitLabEE.gitlab-license", "wb") as f:
            f.write(encrypt_license)
        return encrypt_license.decode()

    def parse(self, licenses):
        encrypt_license = base64.b64decode(licenses)
        encrypt_license = json.loads(encrypt_license.decode())
        encrypt_data = base64.b64decode(
            encrypt_license["data"].replace("\n", "")
        )
        encrypt_key = base64.b64decode(encrypt_license["key"].replace("\n", ""))
        iv = base64.b64decode(encrypt_license["iv"])
        # 原则上不应该使用公钥解密，尽管CryptoPlus支持公钥解密
        key = self.crypto_plus.decrypt_by_public_key(encrypt_key)
        data = AES.new(key, AES.MODE_CBC, iv).decrypt(encrypt_data)
        if data[-1] != 125:
            # 不以}结尾
            data = data[: -data[-1]]
        # print(json.dumps(json.loads(data.decode()), indent=2))
        return json.dumps(json.loads(data.decode()), indent=2)

    def patch(self):
        return ""


if __name__ == "__main__":
    GitlabKeyGen().run()

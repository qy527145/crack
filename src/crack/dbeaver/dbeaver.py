import base64
from time import time

from crypto_plus import CryptoPlus
from crypto_plus.encrypt import decrypt_by_key, encrypt_by_key

from crack.base import KeyGen

# power[Args] 模板
power_args_template = 'EQUAL,65537,{old_n}->65537,{new_n}'


class LicenseItem:
    def __init__(self, value, size):
        self.value = value
        self.size = size

    def __bytes__(self):
        if isinstance(self.value, str):
            return self.value.encode() + b'\x20' * (self.size - len(self.value))
        if isinstance(self.value, int):
            return self.value.to_bytes(self.size)
        if isinstance(self.value, bytes):
            return self.value

    def __or__(self, other):
        if isinstance(other, LicenseItem):
            return LicenseItem(bytes(self) + bytes(other), self.size + other.size)


class License:
    def __init__(self):
        self.format = LicenseItem(1, 1)
        self.license_id = LicenseItem('DB-1Y1MTZFU-ZHGR', 16)
        self.license_type = LicenseItem(b'U'[0], 1)
        self.license_issue_time = LicenseItem(int(time() * 1000), 8)
        self.license_start_time = LicenseItem(int(time() * 1000), 8)
        self.license_end_time = LicenseItem(0, 8)
        self.flags = LicenseItem(1024, 8)
        self.product_id = LicenseItem("dbeaver-ue", 16)
        self.product_version = LicenseItem("22.1", 8)
        self.owner_id = LicenseItem("10000", 16)
        self.owner_company = LicenseItem("void", 64)
        self.owner_name = LicenseItem("xuqiao", 32)
        self.owner_email = LicenseItem("wmymz@icloud.com", 48)
        self.years_number = LicenseItem(1, 1)
        self.reserved1 = LicenseItem(0, 1)
        self.users_number = LicenseItem(1, 2)

    def __bytes__(self):
        return bytes(
            self.format | \
            self.license_id | \
            self.license_type | \
            self.license_issue_time | \
            self.license_start_time | \
            self.license_end_time | \
            self.flags | \
            self.product_id | \
            self.product_version | \
            self.owner_id | \
            self.owner_company | \
            self.owner_name | \
            self.owner_email | \
            self.years_number | \
            self.reserved1 | \
            self.users_number
        )


class DBeaverKeyGen(KeyGen):
    def __init__(self):
        try:
            obj = CryptoPlus.load()
        except Exception:
            obj = CryptoPlus.generate_rsa(2048)
            obj.dump()
        self.crypto_plus = obj

    def generate(self):
        license_info = bytes(License())
        return base64.b64encode(encrypt_by_key(self.crypto_plus.private_key, license_info)).decode()

    def parse(self, licenses):
        return decrypt_by_key(self.crypto_plus.public_key, base64.b64decode(licenses))

    def patch(self):
        with open("dbeaver-ue-public.key", 'r') as f:
            old_n = CryptoPlus.loads(''.join(f.readlines()[1:])).public_key.n
        return power_args_template.format(old_n=old_n, new_n=self.crypto_plus.public_key.n)


if __name__ == '__main__':
    DBeaverKeyGen().run()

import os
import pathlib
import shutil
from base64 import b64encode, b64decode

from asarPy import extract_asar, pack_asar
from crypto_plus import CryptoPlus
from crypto_plus.encrypt import encrypt_by_key, decrypt_by_key

from crack.base import Licenses


class XmindLicenses(Licenses):

    def __init__(self):
        tmp_path = os.environ['TMP']
        asar_path = pathlib.Path(tmp_path).parent.joinpath(r'Programs\Xmind\resources')
        self.asar_file = asar_path.joinpath('app.asar')
        self.asar_file_bak = asar_path.joinpath('app.asar.bak')
        self.crack_asar_dir = asar_path.joinpath('ext')
        self.main_dir = self.crack_asar_dir.joinpath("main")
        self.renderer_dir = self.crack_asar_dir.joinpath("renderer")
        self.private_key = None
        self.public_key = None

        with open("crack/hook/old.pem", 'rb') as f:
            self.old_key = f"String.fromCharCode({','.join([str(i) for i in f.read()])})".encode()

    def generate(self):
        if os.path.isfile('crack/hook/key.pem'):
            rsa = CryptoPlus.load('crack/hook/key.pem')
        else:
            rsa = CryptoPlus.generate_rsa(2048)
            rsa.dump("crack/hook/key.pem", "crack/hook/new.pem")
        license_info = '{"status": "sub", "expireTime": 4093057076000, "ss": "", "deviceId": "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"}'
        license_data = b64encode(encrypt_by_key(rsa.private_key, license_info.encode()))
        # license_data = "TiT1ul64lE+EMrH0ogOPWHZw5r3sE+jU1l2smjmRuvxmqN3v0NPklgJI9ZpGBt3MZ/mRXM+KmmlZy/bXopy74SH7VLeg3Y1aCATUoWsY2O0XXy1I0JtvLsIF+uM6G2oOx8F6f5Wz+Embhg6b9SIF19MBckmXOOfahd0zWJDaxzpAYthagLgakhbG8k7ynXrUmGIaVmxcktxg3hnRgxlwKvJfM56x5lxF+eLY/t4EFBKfk++omYQExwflUwTrwdeP4kbQvNTMGi9v5Nmyg8Nq7w47sfc1zfeg5opDhW47JTzu29EveGXXAxgV88pjQDZMWjL5c+v4PprDSzF+KJGSfA=="
        with open(r"crack\hook\license.bin", "wb") as f:
            f.write(license_data)
        self.public_key = rsa.public_key
        self.private_key = rsa.private_key
        return license_data

    def parse(self, licenses):
        return decrypt_by_key(self.public_key, b64decode(licenses))

    def patch(self):
        # 解包
        extract_asar(str(self.asar_file), str(self.crack_asar_dir))
        shutil.copytree('crack', self.main_dir, dirs_exist_ok=True)
        # 注入
        with open(self.main_dir.joinpath('main.js'), 'rb') as f:
            lines = f.readlines()
            lines[5] = b'require("./hook")\n'
        with open(self.main_dir.joinpath('main.js'), 'wb') as f:
            f.writelines(lines)
        # 替换密钥
        new_key = f"String.fromCharCode({','.join([str(i) for i in self.public_key.export_key()])})".encode()
        for js_file in self.renderer_dir.rglob("*.js"):
            with open(js_file, 'rb') as f:
                byte_str = f.read()
                index = byte_str.find(self.old_key)
                if index != -1:
                    byte_str.replace(self.old_key, new_key)
                    with open(js_file, 'wb') as _f:
                        _f.write(byte_str.replace(self.old_key, new_key))
                    # print(js_file)
                    break
        # 封包
        if self.asar_file_bak.is_file():
            os.remove(self.asar_file_bak)
        os.renames(self.asar_file, self.asar_file_bak)
        pack_asar(self.crack_asar_dir, self.asar_file)
        shutil.rmtree(self.crack_asar_dir)


if __name__ == '__main__':
    XmindLicenses().run()

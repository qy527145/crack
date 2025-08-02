import base64
import pathlib
from Crypto.Cipher import AES


from crack.base import KeyGen

aes_key = bytes.fromhex(
    "4ee1b382949a024b802f52b4b4fe57f1bef40853109256e2c20deca3dd8dd56d"
)


class TyporaKeyGen(KeyGen):
    def __init__(self):
        asar_path = pathlib.Path(r"D:\Program Files\Typora\resources")
        self.asar_file = asar_path.joinpath("app.asar")
        self.asar_file_bak = asar_path.joinpath("app.asar.bak")
        self.crack_asar_dir = asar_path.joinpath("ext")

    def parse(self, licenses):
        pass

    def generate(self):
        pass

    def patch(self):
        # 解包
        # extract_asar(str(self.asar_file), str(self.crack_asar_dir))
        with open(self.crack_asar_dir.joinpath("atom.js")) as f:
            text = f.read()
        aaa = base64.b64decode(text)
        iv = aaa[:16]
        obj = AES.new(aes_key, AES.MODE_CBC, iv=iv)
        obj.decrypt(aaa[16:])
        pass


if __name__ == "__main__":
    TyporaKeyGen().run()

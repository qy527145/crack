import os
import pathlib
import platform
import shutil
from base64 import b64encode

from asarPy import extract_asar, pack_asar
from crypto_plus import CryptoPlus

from crack.base import KeyGen


class XmindKeyGen(KeyGen):
    def __init__(self):
        super().__init__()
        # Get the module directory for storing keys
        module_dir = pathlib.Path(__file__).parent
        key_path = module_dir / "key.pem"
        old_key_path = module_dir / "old.pem"

        if key_path.is_file():
            rsa = CryptoPlus.load(str(key_path))
        else:
            rsa = CryptoPlus.generate_rsa(1024)
            rsa.dump(str(key_path), str(module_dir / "new_public_key.pem"))
        self.crypto_plus = rsa

        # 根据操作系统设置不同的路径
        system = platform.system()
        if system == "Darwin":  # macOS
            asar_path = pathlib.Path("/Applications/Xmind.app/Contents/Resources")
        elif system == "Windows":
            tmp_path = os.environ.get("TMP", os.path.expanduser("~"))
            asar_path = pathlib.Path(tmp_path).parent.joinpath(r"Programs\Xmind\resources")
        else:
            raise OSError(f"Unsupported operating system: {system}")

        self.asar_file = asar_path.joinpath("app.asar")
        self.asar_file_bak = asar_path.joinpath("app.asar.bak")
        self.crack_asar_dir = asar_path.joinpath("ext")
        self.main_dir = self.crack_asar_dir.joinpath("main")
        self.renderer_dir = self.crack_asar_dir.joinpath("renderer")
        self.license_data = None

        if old_key_path.is_file():
            self.old_public_key = old_key_path.read_text()
        else:
            raise FileNotFoundError(f"old.pem not found at {old_key_path}")

    def generate(self):
        license_info = '{"status": "sub", "expireTime": 4093057076000, "ss": "", "deviceId": "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"}'
        self.license_data = b64encode(
            self.crypto_plus.encrypt_by_private_key(license_info.encode())
        )
        return self.license_data

    def parse(self, licenses):
        return self.crypto_plus.decrypt_by_public_key(b64encode(licenses))

    def patch(self):
        # 清理旧的解压目录（如果存在）
        if self.crack_asar_dir.exists():
            shutil.rmtree(self.crack_asar_dir)
        # 解包
        extract_asar(str(self.asar_file), str(self.crack_asar_dir))
        shutil.copytree("crack", self.main_dir, dirs_exist_ok=True)
        # 注入 - 在文件开头插入 require
        with open(self.main_dir.joinpath("main.js"), "rb") as f:
            content = f.read()
        with open(self.main_dir.joinpath("main.js"), "wb") as f:
            f.write(b'require("./hook");\n' + content)
        # 替换密钥
        old_key = f"String.fromCharCode({','.join([str(i) for i in self.old_public_key.encode()])})".encode()
        new_key = f"String.fromCharCode({','.join([str(i) for i in self.crypto_plus.public_key.export_key()])})".encode()
        for js_file in self.renderer_dir.rglob("*.js"):
            with open(js_file, "rb") as f:
                byte_str = f.read()
                index = byte_str.find(old_key)
                if index != -1:
                    byte_str.replace(old_key, new_key)
                    with open(js_file, "wb") as _f:
                        _f.write(byte_str.replace(old_key, new_key))
                    print(js_file)
                    break
        # 占位符填充
        with open(self.main_dir.joinpath("hook.js"), "r", encoding="u8") as f:
            content = f.read()
            content = content.replace("{{license_data}}", self.license_data.decode())
        with open(self.main_dir.joinpath("hook.js"), "w", encoding="u8") as f:
            f.write(content)
        with open(
            self.main_dir.joinpath("hook").joinpath("crypto.js"), "r", encoding="u8"
        ) as f:
            content = f.read()
            content = content.replace(
                "{{old_public_key}}", self.old_public_key.replace("\n", "\\n")
            )
            content = content.replace(
                "{{new_public_key}}",
                self.crypto_plus.public_key.export_key().decode().replace("\n", "\\n"),
            )
        with open(
            self.main_dir.joinpath("hook").joinpath("crypto.js"), "w", encoding="u8"
        ) as f:
            f.write(content)
        # 封包
        os.remove(self.asar_file)
        pack_asar(self.crack_asar_dir, self.asar_file)
        shutil.rmtree(self.crack_asar_dir)


if __name__ == "__main__":
    XmindKeyGen().run()

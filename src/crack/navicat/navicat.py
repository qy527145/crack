import lief, base64, json, time, os
from lief.PE import Binary, Section
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

PE_FILE_PATH = "libcc.dll"

ORIGINAL_BYTECODE = b"".join(
    [
        b"\x48\x8b\xd0\x48\x8b\xcf\xff\xd3\x48\x89\x46\x20\x48\x8b\x55\x10",
        b"\x48\x83\xfa\x0f\x76\x34\x48\xff\xc2\x48\x8b\x4d\xf8\x48\x8b\xc1",
        b"\x48\x81\xfa\x00\x10\x00\x00\x72\x1c\x48\x83\xc2\x27\x48\x8b\x49",
        b"\xf8\x48\x2b\xc1\x48\x83\xc0\xf8\x48\x83",
    ]
)

PATCH_BYTECODE = b"".join(
    [
        b"\x48\x8d\x0d\x00\x00\x00\x00\x48\x89\x08\x48\x89\xc2\x48\x89\xf9",
        b"\xff\xd3\x48\x89\x46\x20\x48\x8b\x55\x10\x90\x90\x90\x90\x90\x90",
        b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90",
        b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90",
        b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90",
    ]
)


def find_bytes(pe_file: str, pattern: bytes) -> int:
    with open(pe_file, "rb") as f:
        data = f.read()
        patch_file_offset = data.find(ORIGINAL_BYTECODE)
        if patch_file_offset == -1:
            raise ValueError("Original bytecode not found in the binary.")
        return patch_file_offset


def add_pkey_section(pe: Binary, public_key: str) -> None:
    pkey_section = Section(".pkey")
    payload = public_key.encode() + b"\0"
    pkey_section.content = list(payload)  # type: ignore
    pkey_section.virtual_size = len(payload)
    pkey_section.characteristics = Section.CHARACTERISTICS.MEM_READ  # type: ignore
    pe.add_section(pkey_section)  # type: ignore


def calc_offset(pe: Binary, patch_file_offset: int) -> int:
    text_scection = pe.get_section(".text")
    pkey_section = pe.get_section(".pkey")

    text_file_offset = text_scection.pointerto_raw_data
    text_virtual_address = text_scection.virtual_address
    pkey_virtual_address = pkey_section.virtual_address
    offset_from_rip = pkey_virtual_address - (text_virtual_address + patch_file_offset - text_file_offset + 7)

    print(".text FOA:", hex(text_file_offset))
    print(".text VA: ", hex(text_virtual_address))
    print(".pkey VA: ", hex(pkey_virtual_address))
    print(f"Patch assembly code: lea rcx, [rip + {hex(offset_from_rip)}]")
    return offset_from_rip


def patch_pe(pe_file: str, patch_file_offset: int) -> None:
    with open(pe_file, "rb+") as f:
        f.seek(patch_file_offset)
        f.write(patch_bytecode)
        print(f"Patched binary written to {pe_file}")


def decrypt_request(reg: str, key: RSA.RsaKey) -> str:
    cipher = PKCS1_v1_5.new(key)
    plain = cipher.decrypt(base64.b64decode(reg), None)
    if plain is None:
        raise ValueError("解密失败，注册信息无效")
    return plain.decode()


def pkcs1_v15_private_pad(message: bytes, key: RSA.RsaKey) -> bytes:
    k = key.size_in_bytes()
    if len(message) > k - 11:
        raise ValueError("message too long for RSA modulus")

    ps_len = k - len(message) - 3
    ps = b'\xFF' * ps_len  # BlockType=1 -> FF 填充
    em = b'\x00\x01' + ps + b'\x00' + message
    return em


def rsa_private_encrypt(message: bytes, key_pem: str) -> str:
    key = RSA.import_key(key_pem)
    em = pkcs1_v15_private_pad(message, key)
    m_int = int.from_bytes(em, 'big')
    c_int = pow(m_int, key.d, key.n)
    return base64.b64encode(c_int.to_bytes(key.size_in_bytes(), 'big')).decode()


if __name__ == "__main__":
    if not os.path.exists(PE_FILE_PATH):
        print(f"PE 文件 {PE_FILE_PATH} 不存在。请在Navicat安装目录下运行此脚本。")
        exit(1)

    print("Navicat 17.3.x 激活补丁脚本")
    print("请先断开网络, 并关闭所有 Navicat 相关进程后再运行此脚本...")
    ask = input("确认继续? (y/n): ").strip().lower()
    if ask != "y" and ask != "yes" and ask != "Y":
        print("操作已取消。")
        exit(0)

    print("开始激活流程...")
    print()

    print("Step 1: 备份源文件")
    backup_path = PE_FILE_PATH + ".bak"
    if not os.path.exists(backup_path):
        os.rename(PE_FILE_PATH, backup_path)
        print(f"已备份为 {backup_path}")
    else:
        print(f"备份文件 {backup_path} 已存在，跳过备份步骤")
    print()

    print("Step 2: 生成自定义密钥对")
    key = RSA.generate(2048)
    priv_pem = key.export_key().decode()
    pub_pem = key.publickey().export_key().decode()
    public_key = "".join(pub_pem.splitlines()[1:-1])
    print("密钥对已生成。")
    print("公钥:")
    print(pub_pem)
    print("私钥:")
    print(priv_pem)
    print()

    print("Step 3: 应用补丁")
    patch_file_offset = find_bytes(backup_path, ORIGINAL_BYTECODE)
    print(f"找到待修补位置: {hex(patch_file_offset)}")
    pe = lief.parse(backup_path)
    assert pe is not None
    assert isinstance(pe, Binary)

    add_pkey_section(pe, public_key)
    offset_from_rip = calc_offset(pe, patch_file_offset)
    patch_bytecode = PATCH_BYTECODE.replace(b"\x00\x00\x00\x00", offset_from_rip.to_bytes(4, byteorder="little"))
    pe.write(PE_FILE_PATH)
    patch_pe(PE_FILE_PATH, patch_file_offset)
    print("补丁应用完成")

    print("Step 4: 不要退出此脚本, 请断网后运行 Navicat, 输入密钥并使用离线激活:")
    print("NAVMIKCHCWNIHS3Q")
    print()
    os.system("start navicat.exe")
    req = input("请输入离线激活请求码:\n").strip()
    plain = decrypt_request(req, key)
    print("解密得到: ", plain)
    print()
    data = json.loads(plain)
    username = input("请输入用户名: ").strip()
    organization = input("请输入组织名: ").strip()
    t = int(time.time())
    data.update({
        "N": username,
        "O": organization,
        "T": t
    })
    msg = json.dumps(data, ensure_ascii=False).encode()
    reg = rsa_private_encrypt(msg, priv_pem).strip()
    print("激活码: \n")
    print(reg)
    print("\n请复制上面的激活码到 Navicat 激活窗口完成激活。")
    os.system("pause")
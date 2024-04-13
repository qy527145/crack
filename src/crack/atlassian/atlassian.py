import base64
import textwrap
import zlib

from crypto_plus import CryptoPlus

key = "MIIBSwIBADCCASwGByqGSM44BAEwggEfAoGBAP1/U4EddRIpUt9KnC7s5Of2EbdSPO9EAMMeP4C2USZpRV1AIlH7WT2NWPq/xfW6MPbLm1Vs14E7gB00b/JmYLdrmVClpJ+f6AR7ECLCT7up1/63xhv4O1fnxqimFQ8E+4P208UewwI1VBNaFpEy9nXzrith1yrv8iIDGZ3RSAHHAhUAl2BQjxUjC8yykrmCouuEC/BYHPUCgYEA9+GghdabPd7LvKtcNrhXuXmUr7v6OuqC+VdMCz0HgmdRWVeOutRZT+ZxBxCBgLRJFnEj6EwoFhO3zwkyjMim4TwWeotUfI0o4KOuHiuzpnWRbqN/C/ohNWLx+2J6ASQ7zKTxvqhRkImog9/hWuWfBpKLZl6Ae1UlZAFMO/7PSSoEFgIUNYsbkapILzW8VhfGrU4eHo6/Dqw="

template_license_data = """
#Thu Dec 21 16:52:17 CST 2023
CreationDate=2023-12-21
Evaluation=false
Description=Unlimited license by https://zhile.io
Organisation=dsa
conf.active=true
ContactEMail=asd
licenseHash=MCwCFDtJo7HY9ptqFsplyRvDIXQPBYqKAhQvSzL+nA2Us6Y6qZ6oo88eoXLpqA==
conf.Starter=false
conf.LicenseTypeName=COMMERCIAL
MaintenanceExpiryDate=2089-07-07
LicenseID=LIDSEN-L1703148737131
ServerID=123456
conf.DataCenter=true
keyVersion=1600708331
LicenseExpiryDate=2089-07-07
PurchaseDate=2023-12-21
licenseVersion=2
Subscription=true
conf.NumberOfUsers=-1
SEN=SEN-L1703148737131
ContactName=asd
"""


def baseN(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):  # noqa
    return ((num == 0) and numerals[0]) or (
            baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b]
    )


def parse(code):
    code = code.strip().replace("\n", "")
    sig_index = code.rfind("X02")
    assert sig_index != -1, "无效激活码"
    code_len = int(code[sig_index + 3:], 31)
    code = code[:sig_index]
    code_bytes = base64.b64decode(code)
    assert len(base64.b64encode(code_bytes)) == code_len, "无效激活码"
    i = int.from_bytes(code_bytes[:4]) + 4
    text_bytes = code_bytes[4:i]
    hash_bytes = code_bytes[i:]

    dsa = CryptoPlus.loads(key)
    assert dsa.verify(text_bytes, hash_bytes, "SHA1"), "无效激活码"
    print(zlib.decompress(text_bytes[5:]).decode())


def generate():
    prefix = b"\x0d\x0e\x0c\x0a\x0f"
    zip_bytes = zlib.compress(template_license_data.strip().encode())
    message = prefix + zip_bytes
    message_head = len(message).to_bytes(4)
    dsa = CryptoPlus.loads(key)
    signature = dsa.sign(message, "SHA1")
    code_bytes = message_head + message + signature

    code_tail = "X02" + baseN(len(base64.b64encode(code_bytes)), 31)
    code = base64.b64encode(code_bytes).decode() + code_tail
    code = "\n".join(textwrap.wrap(code, 76))
    print(code)
    return code


if __name__ == "__main__":
    # zip_buf = zlib.compress(b'asd', wbits=16 + zlib.MAX_WBITS)
    # source = zlib.decompress(zip_buf, 16 + zlib.MAX_WBITS)
    # print(source)
    act_code = """
AAABfg0ODAoPeJxtUVFPszAUfe+vIPEZR4uwuaQPEzDOwPgUZtS3rtxJI+tYW+aHv96OYUyMSe9D7
23POfeci7LunBi4Q7CDp/MgmOPAiYrSIR7xUaSAGbGXMTNATx0XE5dglBxZ0w0TumWNBhSD5kq0Q
2ctG7ETBiqnERykBmfTO7UxrZ5PJp+1aOBS7FGu3pgU+gxSaYb4Xm4vGTfiCNSoDlC0l8bek4yJh
jJdoRHujumaZpEX3Saln04Ok4/2pqrI21KsOI6zW/FxeE0X9XohZgkPfW4evfDQ9S91uS6e8929+
Mwf6JmuMEwZUOMSQys9k5R9Cyu2AxrlWZY8RstFiqwQaUAyySH53wrVj7bMrl1vag8a/y5jmi7jI
lm5KZ56Pg5IYCu8QgWoIyg7xsS/CsIzoQVhEciTjGHtd+ifQOmTLTj0vKk38338Df03779O8Zpp+
B3TaNg3HEFFt/nJaWAbJKy63QZUvl1r+5K6GFnt9A/9YyKDLzaQL1JnulowLAIUXNWpxJYDbAba+
IH9vOa4CE9mebMCFEw1VlpaALNRy6rw78w3wotUn3SKX02ii
    """
    parse(act_code)
    code2 = generate()
    parse(code2)

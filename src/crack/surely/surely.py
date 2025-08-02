import base64
import hashlib


def md5(msg):
    return hashlib.md5(msg).hexdigest()


if __name__ == "__main__":
    # domain = 'your domain'
    domain = "_"
    key = base64.b64encode(
        f"ORDER:00001,EXPIRY=33227712000000,DOMAIN={domain},ULTIMATE=1,KEYVERSION=1".encode()
    )
    sign = md5(key)
    print(f"{sign}{key.decode()}")
    import frida

    frida.attach()

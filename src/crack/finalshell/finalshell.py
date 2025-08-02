from Crypto.Hash import keccak
from Crypto.Hash import MD5


def md5(msg):
    hash_obj = MD5.new(msg)
    return hash_obj.hexdigest()


def keccak384(msg):
    hash_obj = keccak.new(data=msg, digest_bits=384)
    return hash_obj.hexdigest()


if __name__ == "__main__":
    code = input("输入机器码: ")
    print("版本号 < 3.9.6 (旧版)")
    print("高级版:", md5(f"61305{code}8552".encode())[8:24])
    print("专业版:", md5(f"2356{code}13593".encode())[8:24])
    print("版本号 >= 3.9.6 (新版)")
    print("高级版:", keccak384(f"{code}hSf(78cvVlS5E".encode())[12:28])
    print("专业版:", keccak384(f"{code}FF3Go(*Xvbb5s2".encode())[12:28])
    print("版本号 (4.5)")
    print("高级版:", keccak384(f"{code}wcegS3gzA$".encode())[12:28])
    print("专业版:", keccak384(f"{code}b(xxkHn%z);x".encode())[12:28])
    print("版本号 (4.6)")
    print("高级版:", keccak384(f"{code}csSf5*xlkgYSX,y".encode())[12:28])
    print("专业版:", keccak384(f"{code}Scfg*ZkvJZc,s,Y".encode())[12:28])

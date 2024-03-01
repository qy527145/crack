const crypto = require("crypto");
const fs = require("fs");

// 保存原始的 publicDecrypt 函数
const originalPublicDecrypt = crypto.publicDecrypt;
/**
 * 官方公钥解密
 * @param {string} message  密文
 * @returns
 */
const originalPublicDecryptEx = function (message) {
    // let key = `-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCDYH31l0llicBavbUZRg0y1LnI\n2JJuPZak0498wGmK0N+ksqCzA0XUfCgQ5E9itYyPuT+z6Pz/+0q6NeApkWcnC/Th\nWQY6ZlEOMonrhPub8zsWYOZzckQutx3jn6k+6ZXx7yUbbkxIk+wqWgnlQxnx6TMd\nS3rgo3r4blFTWi6EEQIDAQAB\n-----END PUBLIC KEY-----`;
    let key = fs.readFileSync('old.pem', encoding = 'utf8')
    const n = originalPublicDecrypt(
        {
            key: key,
            padding: 1,
        },
        message
    );
    return n;
};

// 将 publicDecrypt 函数定义为 getter 方法，返回新的实现
Object.defineProperty(crypto, "publicDecrypt", {
    get() {
        return function myPublicDecrypt(...args) {
            console.trace("myPublicDecrypt 调用栈");
            console.log("秋城落叶Hook Xmind开始");

            // args[0]["key"] =
            // "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqIGfghxs/schjid+mHlK\nAQhWHm1z1uPX/CWr2TBHPcg3PDmF8vViyhuxpkVe4/X4Tz9hN9BGA+h7toHUw6rK\nz2Mk5M5peG5Id4DVLADuVdpcbjo0Ypc0mOdDDTJtlc2T8q10rdGYD0ErpeR9Su9i\naJxDWMOLlNzpmWXpgKQWjRuzoIrOiiHvGzAiSrCMKt6m+/m+Svr5CQHw+/Jx1iAw\nyMZIMwux8gsgawVtU1u6MmIB9px4JncFepsg3FdSEbqdYZL3MeExDT7PPh2GQcbS\nfcl1gYTrCgJFUZUr2JBOSVIoIvGATH7VIMYBWantbAiQgGqkJstXb8UngEM4hrsX\nuQIDAQAB\n-----END PUBLIC KEY-----";
            args[0]["key"] = fs.readFileSync('new.pem', encoding = 'utf8')
            let result;
            try {
                result = originalPublicDecrypt.call(this, ...args);
                let data = JSON.parse(result.toString());
                // data.status = "sub";
                // data.expireTime = 4093057076000;
                result = Buffer.from(JSON.stringify(data));
                crypto.log("用自己的密钥解密成功，开始走我的密钥解密流程。", data);
            } catch (e) {
                crypto.log("解密出错，开始走官方密钥解密流程。");
                result = null;
                let ori = originalPublicDecryptEx(args[1]);
                crypto.log(
                    "解密出错",
                    args[1].toString("base64"),
                    "\n官方密钥解密结果",
                    ori,
                    "\n错误细节\n",
                    e
                );
                result = ori;
            }

            // 调用原始的 publicDecrypt 函数
            return result;
        };
    },
});

Object.defineProperty(crypto, "log", {
    get() {
        return function log(...args) {
            console.log(...args);
        };
    },
});

module.exports = crypto;

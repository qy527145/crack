const crypto = require("crypto");

// 保存原始的 publicDecrypt 函数
const originalPublicDecrypt = crypto.publicDecrypt;
/**
 * 官方公钥解密
 * @param {string} message  密文
 * @returns
 */
const originalPublicDecryptEx = function (message) {
    let key = `{{old_public_key}}`;
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

            args[0]["key"] = "{{new_public_key}}";
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

const electron = require("electron");

// 获取原始的 net 模块
const originalNet = electron.net;

// 保存原始的 request 函数
const originalRequest = originalNet.request;

// 修改 request 函数
Object.defineProperty(originalNet, "request", {
  get() {
    return function (options, callback) {
      let url = options["url"];
      // options.headers["Authorization"] = "Bearer YOUR_TOKEN";
      if (url.indexOf("/_api/share/vana_map/?lang=zh") > -1 ||
        url.indexOf("/_api/share/maps") > -1 //修复在线图库
      ) {
      } else url = url.replace("https://www.xmind.cn", "http://127.0.0.1:3000");
      options["url"] = url;
      // console.error(
      //   "===== Intercepting net.request with options:",
      //   options,
      //   callback
      // );
      const req = originalRequest(options, callback);

      // 注册 response 事件监听器
      req.on("response", (response) => {
        let data = "";
        response.on(
          "data",
          function (chunk) {
            data += chunk;
            chunk = "FUCKING data";
            this.emit("continue", chunk);
          }.bind(response)
        );
        response.on(
          "end",
          function () {
            // 将数据添加到缓存
            // cache[options.url] = data;
            console.log(
              "===== Intercepting net.request with options:",
              options,
              "Response ----- ",
              data
            );
            this.emit("continue");
          }.bind(response)
        );
      });
      return req;
    };
    return function (options, ...args) {
      // 对 options 进行修改或者添加自己的逻辑
      console.error("===== Intercepting net.request with options:", options);

      // { url: 'https://www.xmind.cn/_res/user_sub_status', method: 'GET' }
      // { url: 'https://www.xmind.cn/_res/devices', method: 'POST' }

      // 调用原始的 request 函数
      return originalRequest.call(this, options, ...args);
    };
  },
});

module.exports = electron;

const http = require("http");
const url = require("url");

const hostname = "127.0.0.1";
const port = 3000;

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const path = parsedUrl.pathname;
    const method = req.method;

    res.setHeader("Content-Type", "application/json; charset=utf-8");

    if (path === "/_res/session" && method === "GET") {
        res.statusCode = 200;
        res.end(
            JSON.stringify({
                uid: "_xmind_1234567890",
                group_name: "",
                phone: "18888888888",
                group_logo: "",
                user: "_xmind_1234567890",
                cloud_site: "cn",
                expireDate: 4093057076000,
                emailhash: "1234567890",
                userid: 1234567890,
                if_cxm: 0,
                _code: 200,
                token: "1234567890",
                limit: 0,
                primary_email: "wmymz@icloud.com",
                fullname: "wmymz",
                type: null,
            })
        );
    } else if (path === "/_api/check_vana_trial" && method === "POST") {
        res.statusCode = 200;
        res.end(JSON.stringify({code: 200, _code: 200}));
    } else if (path === "/_res/get-vana-price" && method === "GET") {
        res.statusCode = 200;
        res.end(
            JSON.stringify({
                products: [
                    {month: 6, price: {cny: 0, usd: 0}, type: "bundle"},
                    {month: 12, price: {cny: 0, usd: 0}, type: "bundle"},
                ],
                code: 200,
                _code: 200,
            })
        );
    } else if (path === "/_api/events" && method === "GET") {
        res.statusCode = 200;
        res.end(JSON.stringify({code: 200, _code: 200}));
    } else if (path === "/_res/user_sub_status" && method === "GET") {
        res.statusCode = 200;
        res.end(JSON.stringify({_code: 200}));
    } else if (path === "/piwik.php" && method === "POST") {
        res.statusCode = 200;
        res.end(JSON.stringify({code: 200, _code: 200}));
    } else if (path.startsWith("/_res/token/") && method === "POST") {
        res.statusCode = 200;
        res.end(
            JSON.stringify({
                uid: "_xmind_1234567890",
                group_name: "",
                phone: "18888888888",
                group_logo: "",
                user: "_xmind_1234567890",
                cloud_site: "cn",
                expireDate: 4093057076000,
                emailhash: "1234567890",
                userid: 1234567890,
                if_cxm: 0,
                _code: 200,
                token: "1234567890",
                limit: 0,
                primary_email: "wmymz@icloud.com",
                fullname: "wmymz",
                type: null,
            })
        );
    } else if (path === "/_res/devices" && method === "POST") {
        res.statusCode = 200;
        res.end(
            JSON.stringify({
                raw_data: "{{license_data}}",
                license: {
                    status: "sub",
                    expireTime: 4093057076000,
                },
                _code: 200,
            })
        );
    } else {
        res.statusCode = 404;
        res.end("Not Found");
    }
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});

require("./hook/crypto");
require("./hook/electron");
// require("./hook");

const http = require("node:http");
const { status } = require("./status");

const port = Number(process.env.PORT || 8080);

const server = http.createServer((req, res) => {
  if (req.url === "/healthz") {
    res.writeHead(200, { "content-type": "text/plain" });
    res.end("ok");
    return;
  }
  if (req.url === "/api/status") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(status()));
    return;
  }
  res.writeHead(404);
  res.end();
});

if (require.main === module) {
  server.listen(port, () => console.log(`status-page listening on ${port}`));
}

module.exports = { server };

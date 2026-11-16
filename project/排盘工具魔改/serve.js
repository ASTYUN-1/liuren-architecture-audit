const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = __dirname;

http.createServer((req, res) => {
  let url = req.url.split('?')[0];
  if (url === '/') url = '/index.html';
  const filePath = path.join(ROOT, url);
  if (!fs.existsSync(filePath)) {
    res.writeHead(404);
    return res.end('Not found: ' + url);
  }
  const ext = path.extname(filePath);
  const mime = {
    '.html': 'text/html;charset=utf-8',
    '.js': 'application/javascript;charset=utf-8',
    '.css': 'text/css;charset=utf-8',
    '.svg': 'image/svg+xml',
    '.json': 'application/json',
    '.ico': 'image/x-icon',
  };
  res.writeHead(200, { 'Content-Type': mime[ext] || 'text/plain;charset=utf-8' });
  fs.createReadStream(filePath).pipe(res);
}).listen(3456, () => {
  console.log('Server: http://localhost:3456');
});

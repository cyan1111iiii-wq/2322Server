# Python Multi-threaded Web Server

## Overview
A simple HTTP/1.1 web server implemented in Python using sockets and threading.

## Features
- Multi-threaded (one thread per client)
- Supports GET and HEAD methods
- Handles:
  - 200 OK
  - 400 Bad Request
  - 403 Forbidden
  - 404 File Not Found
  - 304 Not Modified
- Supports text and image files
- Persistent connections (keep-alive & close)
- Caching with Last-Modified and If-Modified-Since
- Basic security (prevents '..' path traversal)
- Request logging

## Run
```bash
python server.py
```

Open browser:
http://127.0.0.1:3000

## Files
- server.py
- index.html
- log.txt

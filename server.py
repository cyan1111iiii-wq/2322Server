import mimetypes
import socket
import threading
import datetime
import os
import time

#host's address and port
HOST = '127.0.0.1'
PORT = 3000

#creat socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind address
server_socket.bind((HOST, PORT))

#start listen
server_socket.listen(5)
print("Waiting for connection")
print(f"Server running on http://{HOST}:{PORT}")

def handle_client(client_socket, addr):
    status_code=200
    print(f"Got connection from {addr}")
    while True:
        # receive require
        request = client_socket.recv(1024).decode()
        if not request or not request.strip():
            break

        print(f"--Received--\n {request}")
        print("--Request End--")

        # Parse request line
        try:
            request_line = request.split('\n')[0]
            method, path, version = request_line.split()
            if method not in ["GET", "HEAD"]:
                response = f"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                client_socket.send(response.encode())
                client_socket.close()
                return
        except:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            client_socket.send(response.encode())
            client_socket.close()
            return
        headers = request.split("\r\n")
        if_modified_since = None
        connect_type = "close"
        for header in headers:
            if header.lower().startswith("connection"):
                if "keep-alive" in header.lower():
                    connect_type = "keep-alive"
            if "If-Modified-Since" in header:
                if_modified_since = header.split(": ", 1)[1]
        # path
        if path == '/':
            path = "/index.html"

        if path == "/favicon.ico":
            response = f"HTTP/1.1 404 File Not Found\r\nContent-Length: 0\r\n\r\n"
            client_socket.send(response.encode())
            continue
        print("Requested path:", path)

        if ".." in path:
            response = f"""HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"""
            client_socket.send(response.encode())
            client_socket.close()
            return

        file_path = path.lstrip("/")

        try:
            # get modified time of the file
            last_modified_time = os.path.getmtime(file_path)
            last_modified_str = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(last_modified_time))
            if method == "GET" and if_modified_since is not None:
                if if_modified_since == last_modified_str:
                    response = f"""HTTP/1.1 304 Not Modified\r\nContent-Length: 0\r\nConnection: {connect_type}\r\n\r\n"""
                    client_socket.send(response.encode())
                    continue

            # open file
            with open(file_path, 'rb') as f:
                content = f.read()
            # response successfully
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = "application/octet-stream"

            header = f"""HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nLast-Modified: {last_modified_str}\r\nContent-Length: {len(content)}\r\nConnection: {connect_type}\r\n\r\n"""

            if method == "GET":
                client_socket.send(header.encode() + content)
            elif method == "HEAD":
                client_socket.send(header.encode())

            with open("log.txt", "a") as log:
                log.write(f"{addr[0]} [{datetime.datetime.now()}] {path} {status_code}\n")

        except FileNotFoundError:
            # 404
            status_code = 404
            response = "HTTP/1.1 404 File Not Found\r\nContent-Length: 0\r\n\r\n"
            client_socket.send(response.encode())

            with open("log.txt", "a") as log:
                log.write(f"{addr[0]} [{datetime.datetime.now()}] {path} {status_code}\n")

        # close connection
        if connect_type == "close":
            break
    client_socket.close()


while True:
    #accept connection
    client_socket, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.start()

import socket, threading, select

def forward(src, dst):
    try:
        while True:
            r, _, _ = select.select([src], [], [], 60)
            if not r: break
            data = src.recv(16384)
            if not data: break
            dst.sendall(data)
    except:
        pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def handle(client):
    try:
        server = socket.socket()
        server.settimeout(5)
        server.connect(('192.168.42.76', 80))
        threading.Thread(target=forward, args=(client, server), daemon=True).start()
        threading.Thread(target=forward, args=(server, client), daemon=True).start()
    except Exception as e:
        client.close()

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 8080))
    s.listen(50)
    print("Proxy listening on port 8080 -> 192.168.42.76:80", flush=True)
    while True:
        c, _ = s.accept()
        threading.Thread(target=handle, args=(c,), daemon=True).start()

if __name__ == '__main__':
    main()

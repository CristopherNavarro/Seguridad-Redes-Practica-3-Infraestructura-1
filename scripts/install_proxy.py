import subprocess

proxy_code = '''import socket
import threading

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def proxy_port(listen_port, target_ip, target_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', listen_port))
    server.listen(10)
    print(f"Proxy listening on {listen_port} -> {target_ip}:{target_port}", flush=True)
    while True:
        client_sock, _ = server.accept()
        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            target_sock.connect((target_ip, target_port))
            t1 = threading.Thread(target=forward, args=(client_sock, target_sock), daemon=True)
            t2 = threading.Thread(target=forward, args=(target_sock, client_sock), daemon=True)
            t1.start()
            t2.start()
        except:
            client_sock.close()

if __name__ == "__main__":
    t = threading.Thread(target=proxy_port, args=(8080, "192.168.42.76", 80), daemon=True)
    t.start()
    proxy_port(8443, "192.168.42.76", 443)
'''

with open("fgt_proxy.py", "w") as f:
    f.write(proxy_code)

# Copy to GNS3 VM via scp
subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", "fgt_proxy.py", "gns3@192.168.6.129:/home/gns3/fgt_proxy.py"], check=True)

# Flush any old PREROUTING rules for 8080 and 8443, then run proxy
cmd = (
    "sudo iptables -t nat -F PREROUTING && "
    "pkill -f fgt_proxy.py || true && "
    "nohup python3 /home/gns3/fgt_proxy.py > /tmp/proxy.log 2>&1 & sleep 1 && "
    "cat /tmp/proxy.log"
)
res = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "gns3@192.168.6.129", cmd], capture_output=True, text=True)
print("Output:\n", res.stdout)
print("Stderr:\n", res.stderr)

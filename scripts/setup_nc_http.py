import telnetlib
import time

HOST = "192.168.6.129"

def start_http_listener(name, port, title, desc):
    print(f"[*] Configurando HTTP en {name} (puerto {port})...")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    tn.read_very_eager()
    
    html = f"<html><body><h1>{title}</h1><p>{desc}</p></body></html>"
    length = len(html.encode('utf-8'))
    response = f"HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nContent-Length: {length}\\r\\nConnection: close\\r\\n\\r\\n{html}"
    
    script_sh = f"""cat << 'EOF' > /root/http_srv.sh
#!/bin/sh
while true; do
    echo -e "{response}" | nc -l -p 80
    sleep 0.1
done
EOF
chmod +x /root/http_srv.sh
pkill -f http_srv.sh 2>/dev/null
killall nc 2>/dev/null
/root/http_srv.sh > /dev/null 2>&1 &
sleep 1
"""
    for line in script_sh.strip().splitlines():
        tn.write(line.encode('ascii') + b"\r\n")
        time.sleep(0.2)
        
    time.sleep(1)
    tn.write(b"netstat -tuln\r\n")
    time.sleep(1)
    print("Netstat:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    
    tn.write(b"wget -q -O - http://127.0.0.1\r\n")
    time.sleep(1)
    print("Local wget test:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    
    # Also start SSH dummy response on port 22
    ssh_cmd = "while true; do echo 'SSH-2.0-OpenSSH_8.9' | nc -l -p 22; sleep 0.1; done &"
    tn.write(ssh_cmd.encode('ascii') + b"\r\n")
    time.sleep(0.5)
    tn.close()

if __name__ == "__main__":
    start_http_listener(
        "Srv-Web-Caja", 5006, 
        "SISTEMA DE FACTURACION Y CAJA", 
        "Acceso Autorizado para Usuarios LAN."
    )
    start_http_listener(
        "Srv-Web-Inventario", 5008, 
        "SISTEMA DE INVENTARIO CENTRAL", 
        "Acceso Confidencial y Restringido."
    )
    # Also for Srv-DB
    tn = telnetlib.Telnet(HOST, 5010, timeout=5)
    time.sleep(0.5)
    tn.write(b"killall nc 2>/dev/null; while true; do echo 'SSH-2.0-OpenSSH_8.9 Srv-DB' | nc -l -p 22; sleep 0.1; done &\r\n")
    time.sleep(0.5)
    tn.write(b"while true; do echo '5.7.34-MySQL-Server' | nc -l -p 3306; sleep 0.1; done &\r\n")
    time.sleep(0.5)
    tn.close()
    print("[+] Todos los servicios iniciados correctamente.")

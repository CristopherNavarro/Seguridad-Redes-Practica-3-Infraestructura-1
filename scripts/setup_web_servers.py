import telnetlib
import time

HOST = "192.168.6.129"

def setup_server(name, port, html_content):
    print(f"[*] Configurando servicio Web en {name} (puerto {port})...")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    tn.read_very_eager()
    
    # Check if python3 is available or use busybox httpd
    tn.write(b"which python3; which httpd\r\n")
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Tools available:\n", out)
    
    cmds = [
        "mkdir -p /var/www/localhost/htdocs",
        f"cat << 'EOF' > /var/www/localhost/htdocs/index.html\n{html_content}\nEOF",
        "killall httpd 2>/dev/null",
        "httpd -h /var/www/localhost/htdocs -p 80",
        "netstat -tuln"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.5)
        
    time.sleep(1)
    status = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Server Status:\n", status)
    
    # Test local curl
    tn.write(b"wget -q -O - http://127.0.0.1\r\n")
    time.sleep(1)
    print("Local wget test:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

if __name__ == "__main__":
    html_caja = "<html><head><title>Sistema de Caja</title></head><body><h1>SISTEMA DE FACTURACION Y CAJA</h1><p>Bienvenido. Estado: AUTORIZADO Y OPERATIVO.</p></body></html>"
    html_inv = "<html><head><title>Sistema de Inventario</title></head><body><h1>SISTEMA DE INVENTARIO CENTRAL</h1><p>ACCESO CONFIDENCIAL Y RESTRINGIDO A PERSONAL AUTORIZADO.</p></body></html>"
    
    setup_server("Srv-Web-Caja", 5006, html_caja)
    setup_server("Srv-Web-Inventario", 5008, html_inv)

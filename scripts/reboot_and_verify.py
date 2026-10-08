import telnetlib
import time

HOST = "192.168.6.129"

def wait_and_verify():
    print("[*] Esperando arranque de FGT1 tras reconexión...")
    start = time.time()
    while time.time() - start < 120:
        try:
            tn = telnetlib.Telnet(HOST, 5000, timeout=3)
            time.sleep(1)
            tn.write(b"\r")
            time.sleep(1)
            buf = tn.read_very_eager().decode('ascii', errors='ignore')
            tn.close()
            if "login:" in buf.lower() or "#" in buf:
                print("[+] FGT1 está listo!")
                break
            else:
                last_line = [l.strip() for l in buf.splitlines() if l.strip()]
                if last_line:
                    print(f"Booting: {last_line[-1][:60]}")
        except Exception:
            pass
        time.sleep(5)

    # Login to FGT1
    print("[*] Iniciando sesión en FGT1...")
    tn = telnetlib.Telnet(HOST, 5000, timeout=10)
    time.sleep(1)
    tn.write(b"\r")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    if "login:" in buf.lower():
        tn.write(b"admin\r")
        time.sleep(1)
        tn.write(b"Fortinet2025!\r")
        time.sleep(1.5)
    elif "password:" in buf.lower():
        tn.write(b"Fortinet2025!\r")
        time.sleep(1.5)
        
    tn.write(b"config system console\rset output standard\rend\r")
    time.sleep(1)
    tn.read_very_eager()

    # Check physical interfaces
    print("\n=== Estado de Interfaces Físicas ===")
    tn.write(b"get system interface physical\r")
    time.sleep(1.5)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))

    # Ping DMZ Web Server Caja
    print("\n=== Prueba de Ping a DMZ Srv-Web-Caja (10.25.9.2) ===")
    tn.write(b"execute ping-options source 10.25.9.1\r")
    time.sleep(0.5)
    tn.write(b"execute ping 10.25.9.2\r")
    time.sleep(2)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))

    # Check WAN port1 IP
    print("\n=== IP en port1 (WAN) ===")
    tn.write(b"diagnose ip address list\r")
    time.sleep(1)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

if __name__ == "__main__":
    wait_and_verify()

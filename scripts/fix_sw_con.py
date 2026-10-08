import telnetlib
import time

HOST = "192.168.6.129"

for name, port in [("SW1", 5002), ("SW2", 5004)]:
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    if "Username:" in buf:
        tn.write(b"admin\r\n")
        time.sleep(0.5)
        tn.write(b"Cisco123!\r\n")
        time.sleep(1)
    elif ">" in buf:
        tn.write(b"enable\r\nCisco123!\r\n")
        time.sleep(0.5)
        
    cmds = [
        "configure terminal",
        "line con 0",
        " privilege level 15",
        " no login",
        " logging synchronous",
        "end",
        "write memory"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.2)
    time.sleep(1)
    tn.close()
    print(f"[+] {name} console configurado para acceso directo en modo privilegiado.")

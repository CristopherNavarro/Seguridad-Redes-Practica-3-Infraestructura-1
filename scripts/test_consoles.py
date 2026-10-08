import telnetlib
import time

nodes = {
    "FGT1": 5000,
    "SW1": 5002,
    "SW2": 5004,
    "Srv-Web-Caja": 5006,
    "Srv-Web-Inventario": 5008,
    "Srv-DB": 5010,
    "PC1-VLAN10": 5012,
    "PC2-VLAN20": 5014
}

for name, port in nodes.items():
    try:
        tn = telnetlib.Telnet("192.168.6.129", port, timeout=3)
        time.sleep(0.5)
        tn.write(b"\r\n")
        time.sleep(0.5)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        print(f"[{name}] (Port {port}): Connected! Output snippet: {repr(buf[-60:] if len(buf) > 60 else repr(buf))}")
        tn.close()
    except Exception as e:
        print(f"[{name}] (Port {port}): Failed - {e}")

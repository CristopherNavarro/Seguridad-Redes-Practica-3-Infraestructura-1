import telnetlib
import time

for name, port in [("SW1", 5002), ("SW2", 5004)]:
    tn = telnetlib.Telnet("192.168.6.129", port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    print(f"{name} Buffer:")
    print(repr(buf))
    tn.close()

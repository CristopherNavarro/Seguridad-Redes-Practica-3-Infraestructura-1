import telnetlib
import time

tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=5)
time.sleep(1)
tn.write(b"\r\n")
time.sleep(1)
buf = tn.read_very_eager().decode('ascii', errors='ignore')
print("FGT1 Buffer:")
print(repr(buf))
tn.close()

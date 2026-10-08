import telnetlib
import time

tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=5)
time.sleep(0.5)
tn.write(b"\r\n")
time.sleep(0.5)
buf = tn.read_very_eager().decode('ascii', errors='ignore')
if "login:" in buf:
    tn.write(b"admin\rFortinet2025!\r")
    time.sleep(1)
tn.write(b"config system console\rset output standard\rend\r")
time.sleep(0.5)
tn.read_very_eager()

tn.write(b"show system global\r")
time.sleep(1)
print("System Global:\n", tn.read_very_eager().decode('ascii', errors='ignore'))

tn.write(b"show system interface port1\r")
time.sleep(1)
print("Interface port1:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
tn.close()

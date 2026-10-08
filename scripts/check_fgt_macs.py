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

tn.write(b"get system interface physical\r")
time.sleep(1)
print("Physical interfaces in FortiOS:\n", tn.read_very_eager().decode('ascii', errors='ignore'))

for p in ["port1", "port2", "port3", "port4"]:
    tn.write(f"diagnose hardware deviceinfo nic {p}\r".encode('ascii'))
    time.sleep(0.5)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    for line in out.splitlines():
        if "Permanent HW addr" in line or "Current HW addr" in line or "Speed" in line or "Link" in line:
            print(f"{p}: {line.strip()}")

tn.close()

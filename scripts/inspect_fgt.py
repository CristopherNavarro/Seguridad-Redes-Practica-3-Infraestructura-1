import telnetlib
import time

tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=5)
time.sleep(0.5)
tn.write(b"\x03\r\n\x03\r\n")
time.sleep(1)
buf = tn.read_very_eager().decode('ascii', errors='ignore')
print("Initial buffer:")
print(repr(buf))

if "login:" in buf.lower():
    print("Sending admin...")
    tn.write(b"admin\r\n")
    time.sleep(1)
    buf2 = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Buffer after admin:")
    print(repr(buf2))
    if "password:" in buf2.lower():
        print("Sending blank password...")
        tn.write(b"\r\n")
        time.sleep(1.5)
        buf3 = tn.read_very_eager().decode('ascii', errors='ignore')
        print("Buffer after blank password:")
        print(repr(buf3))
        if "new password" in buf3.lower():
            print("Setting Fortinet2025!...")
            tn.write(b"Fortinet2025!\r\n")
            time.sleep(1)
            tn.write(b"Fortinet2025!\r\n")
            time.sleep(2)
            print("Buffer after setting password:")
            print(repr(tn.read_very_eager().decode('ascii', errors='ignore')))
        elif "login failed" in buf3.lower() or "password:" in buf3.lower():
            print("Trying Fortinet2025! as existing password...")
            tn.write(b"admin\r\n")
            time.sleep(1)
            tn.write(b"Fortinet2025!\r\n")
            time.sleep(2)
            print("Buffer after Fortinet2025!:")
            print(repr(tn.read_very_eager().decode('ascii', errors='ignore')))

tn.write(b"\r\nget system status\r\n")
time.sleep(1.5)
print("System status:")
print(tn.read_very_eager().decode('ascii', errors='ignore'))
tn.close()

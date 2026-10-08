import telnetlib
import time

tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=10)
time.sleep(1)
tn.write(b"\x03\r\x03\r")
time.sleep(1)

# Wake up and get to login
tn.write(b"\r")
time.sleep(1)
buf = tn.read_very_eager().decode('ascii', errors='ignore')
print("Wake buffer:", repr(buf))

if "login:" in buf.lower():
    print("Writing admin\\r ...")
    tn.write(b"admin\r")
    time.sleep(1)
    buf2 = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Buffer after admin:", repr(buf2))
    
    if "new password:" in buf2.lower():
        print("Writing Fortinet2025!\\r for New Password...")
        tn.write(b"Fortinet2025!\r")
        time.sleep(1)
        buf3 = tn.read_very_eager().decode('ascii', errors='ignore')
        print("Buffer after New Password:", repr(buf3))
        
        if "confirm password:" in buf3.lower():
            print("Writing Fortinet2025!\\r for Confirm Password...")
            tn.write(b"Fortinet2025!\r")
            time.sleep(2)
            buf4 = tn.read_very_eager().decode('ascii', errors='ignore')
            print("Buffer after Confirm Password:", repr(buf4))

tn.write(b"\rget system status\r")
time.sleep(1.5)
out = tn.read_very_eager().decode('ascii', errors='ignore')
print("Status output:\n", out)
tn.close()

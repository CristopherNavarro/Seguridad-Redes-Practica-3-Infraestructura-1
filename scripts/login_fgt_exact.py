import telnetlib
import time

def login_fgt():
    tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=10)
    time.sleep(1)
    tn.write(b"\x03\r\n\x03\r\n")
    time.sleep(1)
    
    # Read until login
    res = tn.read_until(b"login: ", timeout=5)
    print("Read until login:", repr(res))
    tn.write(b"admin\r\n")
    
    res = tn.read_until(b"Password: ", timeout=5)
    print("Read until Password:", repr(res))
    tn.write(b"\r\n")
    
    res = tn.read_until(b"New Password: ", timeout=5)
    print("Read until New Password:", repr(res))
    tn.write(b"Fortinet2025!\r\n")
    
    res = tn.read_until(b"Confirm Password: ", timeout=5)
    print("Read until Confirm Password:", repr(res))
    tn.write(b"Fortinet2025!\r\n")
    
    time.sleep(2)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Buffer after password change:\n", buf)
    
    tn.write(b"get system status\r\n")
    time.sleep(1.5)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Status output:\n", out)
    tn.close()

if __name__ == "__main__":
    login_fgt()

import telnetlib
import time

def login_exact_4step():
    tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=10)
    time.sleep(1)
    tn.write(b"\x03\r")
    time.sleep(1)
    
    # 1. Wait for login:
    tn.write(b"\r")
    time.sleep(0.5)
    buf = tn.read_until(b"login: ", timeout=5)
    print("1. Saw login:", repr(buf))
    tn.write(b"admin\r")
    
    # 2. Wait for Password:
    buf2 = tn.read_until(b"Password: ", timeout=5)
    print("2. Saw Password:", repr(buf2))
    tn.write(b"\r")
    
    # 3. Wait for New Password:
    buf3 = tn.read_until(b"New Password: ", timeout=5)
    print("3. Saw New Password:", repr(buf3))
    tn.write(b"Fortinet2025!\r")
    
    # 4. Wait for Confirm Password:
    buf4 = tn.read_until(b"Confirm Password: ", timeout=5)
    print("4. Saw Confirm Password:", repr(buf4))
    tn.write(b"Fortinet2025!\r")
    
    # 5. Check prompt
    time.sleep(2)
    buf5 = tn.read_very_eager().decode('ascii', errors='ignore')
    print("5. Prompt after login:\n", repr(buf5))
    
    tn.write(b"get system status\r")
    time.sleep(1.5)
    print("6. System status:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

if __name__ == "__main__":
    login_exact_4step()

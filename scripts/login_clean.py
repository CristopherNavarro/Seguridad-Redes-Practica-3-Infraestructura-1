import telnetlib
import time

def login_clean():
    tn = telnetlib.Telnet("192.168.6.129", 5000, timeout=10)
    time.sleep(1)
    # Clear screen / wake
    tn.write(b"\x03\r")
    time.sleep(1)
    
    # Read until login
    tn.write(b"\r")
    time.sleep(0.5)
    buf = tn.read_until(b"login: ", timeout=5)
    print("Saw login prompt:", repr(buf))
    
    # Send username
    tn.write(b"admin\r")
    time.sleep(1)
    
    # Read until New Password prompt
    buf2 = tn.read_until(b"New Password: ", timeout=5)
    print("Saw New Password prompt:", repr(buf2))
    
    # Send New Password
    tn.write(b"Fortinet2025!\r")
    time.sleep(1)
    
    # Read until Confirm Password prompt
    buf3 = tn.read_until(b"Confirm Password: ", timeout=5)
    print("Saw Confirm Password prompt:", repr(buf3))
    
    # Send Confirm Password
    tn.write(b"Fortinet2025!\r")
    time.sleep(2)
    
    # Read prompt
    buf4 = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Prompt after confirmation:\n", repr(buf4))
    
    # Test command
    tn.write(b"get system status\r")
    time.sleep(1.5)
    print("System status:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

if __name__ == "__main__":
    login_clean()

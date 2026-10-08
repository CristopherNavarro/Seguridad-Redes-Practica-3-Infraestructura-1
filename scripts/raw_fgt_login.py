import socket
import time

s = socket.socket()
s.connect(("192.168.6.129", 5000))
s.settimeout(3)

def read_all():
    out = b""
    while True:
        try:
            c = s.recv(1024)
            if not c:
                break
            out += c
        except socket.timeout:
            break
    return out.decode('ascii', errors='ignore')

# Send enters to wake
s.sendall(b"\x03\r\n\x03\r\n")
time.sleep(1)
print("Initial:", repr(read_all()))

# Send admin
s.sendall(b"admin\r\n")
time.sleep(1)
res = read_all()
print("After admin:", repr(res))

if "password:" in res.lower():
    # Try Fortinet2025! first
    print("Testing Fortinet2025!...")
    s.sendall(b"Fortinet2025!\r\n")
    time.sleep(1.5)
    res2 = read_all()
    print("After Fortinet2025!:", repr(res2))
    
    if "new password" in res2.lower():
        print("Forced to change password! Sending new password...")
        s.sendall(b"Fortinet2025!\r\n")
        time.sleep(1)
        res3 = read_all()
        print("After new password:", repr(res3))
        s.sendall(b"Fortinet2025!\r\n")
        time.sleep(1)
        print("After confirm:", repr(read_all()))
    elif "login incorrect" in res2.lower():
        print("Fortinet2025! was incorrect. Trying blank password...")
        s.sendall(b"admin\r\n")
        time.sleep(1)
        read_all()
        s.sendall(b"\r\n") # blank
        time.sleep(1)
        res_blank = read_all()
        print("After blank:", repr(res_blank))
        if "new password" in res_blank.lower():
            s.sendall(b"Fortinet2025!\r\n")
            time.sleep(1)
            print("After new:", repr(read_all()))
            s.sendall(b"Fortinet2025!\r\n")
            time.sleep(1)
            print("After confirm:", repr(read_all()))

s.sendall(b"\r\nget system status\r\n")
time.sleep(1)
print("Final check:\n", read_all())
s.close()

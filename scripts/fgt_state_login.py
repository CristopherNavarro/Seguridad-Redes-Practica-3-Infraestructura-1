import telnetlib
import time

def fgt_login(port=5000):
    tn = telnetlib.Telnet("192.168.6.129", port, timeout=10)
    time.sleep(1)
    tn.write(b"\x03\r\x03\r")
    time.sleep(0.5)
    
    logged_in = False
    for step in range(15):
        tn.write(b"\r")
        time.sleep(1)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        print(f"Step {step} buffer:\n{buf}")
        
        if "#" in buf:
            print("[+] LOGGED IN SUCCESSFULLY!")
            logged_in = True
            break
        elif "confirm password:" in buf.lower():
            print("Sending Fortinet2025! to Confirm Password")
            tn.write(b"Fortinet2025!\r")
        elif "new password:" in buf.lower():
            print("Sending Fortinet2025! to New Password")
            tn.write(b"Fortinet2025!\r")
        elif "password:" in buf.lower():
            print("Sending Enter to blank Password")
            tn.write(b"\r")
        elif "login:" in buf.lower():
            print("Sending admin to login")
            tn.write(b"admin\r")
        time.sleep(1.5)
        
    if logged_in:
        tn.write(b"get system status\r")
        time.sleep(1.5)
        print("Status output:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

if __name__ == "__main__":
    fgt_login()

import telnetlib
import time

def wait_for_cisco(name, port, max_wait=120):
    start = time.time()
    print(f"Waiting for {name} on port {port}...")
    while time.time() - start < max_wait:
        try:
            tn = telnetlib.Telnet("192.168.6.129", port, timeout=3)
            time.sleep(1)
            tn.write(b"\r\n\r\n")
            time.sleep(1)
            buf = tn.read_very_eager().decode('ascii', errors='ignore')
            tn.close()
            if ">" in buf or "#" in buf or "initial configuration dialog" in buf or "Press RETURN" in buf:
                print(f"{name} is READY!")
                return True
        except Exception:
            pass
        time.sleep(5)
    print(f"{name} timed out!")
    return False

def wait_for_fortigate(port=5000, max_wait=180):
    start = time.time()
    print(f"Waiting for FortiGate on port {port}...")
    while time.time() - start < max_wait:
        try:
            tn = telnetlib.Telnet("192.168.6.129", port, timeout=3)
            time.sleep(1)
            tn.write(b"\r\n")
            time.sleep(1)
            buf = tn.read_very_eager().decode('ascii', errors='ignore')
            tn.close()
            if "login:" in buf or "FortiGate" in buf or "#" in buf:
                print("FortiGate is READY!")
                return True
            else:
                last_line = [l.strip() for l in buf.splitlines() if l.strip()]
                if last_line:
                    print(f"FortiGate booting: {last_line[-1][:60]}")
        except Exception:
            pass
        time.sleep(6)
    print("FortiGate timed out!")
    return False

if __name__ == "__main__":
    wait_for_cisco("SW1", 5002)
    wait_for_cisco("SW2", 5004)
    wait_for_fortigate(5000)

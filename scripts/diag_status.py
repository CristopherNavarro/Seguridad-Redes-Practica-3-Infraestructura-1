import telnetlib
import time

HOST = "192.168.6.129"

def query(name, port, cmds):
    print(f"\n=================== {name} (Port {port}) ===================")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    if ">" in buf:
        tn.write(b"enable\r\nCisco123!\r\n")
        time.sleep(0.5)
    elif "login:" in buf:
        tn.write(b"admin\r\nFortinet2025!\r\n")
        time.sleep(1)
    tn.write(b"terminal length 0\r\n")
    time.sleep(0.2)
    tn.read_very_eager()
    
    for c in cmds:
        print(f"--- Command: {c} ---")
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(1)
        out = tn.read_very_eager().decode('ascii', errors='ignore')
        print(out)
    tn.close()

if __name__ == "__main__":
    query("SW1", 5002, ["show ip int brief", "show interfaces trunk", "show vlan brief"])
    query("SW2", 5004, ["show ip int brief", "show vlan brief", "show interfaces status"])
    query("FGT1", 5000, ["get system interface", "diagnose ip address list"])
    query("Srv-Web-Caja", 5006, ["ip a", "ip r", "ping -c 2 10.25.9.1"])

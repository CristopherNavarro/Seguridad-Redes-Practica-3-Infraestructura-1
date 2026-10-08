import telnetlib
import time

HOST = "192.168.6.129"

def check():
    # 1. Check FortiGate Interfaces & DHCP
    print("=== FortiGate Interfaces & DHCP Config ===")
    tn = telnetlib.Telnet(HOST, 5000, timeout=5)
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
    
    tn.write(b"show system interface VLAN10_USERS\r")
    time.sleep(1)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))

    tn.write(b"show system interface VLAN20_ADMIN\r")
    time.sleep(1)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))

    tn.write(b"show system interface port3\r")
    time.sleep(1)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))

    tn.write(b"show system dhcp server\r")
    time.sleep(1)
    print(tn.read_very_eager().decode('ascii', errors='ignore'))

    tn.close()

    # 2. Check SW1 Spanning Tree & Port Security
    print("=== SW1 Spanning-Tree & Port Security ===")
    tn2 = telnetlib.Telnet(HOST, 5002, timeout=5)
    time.sleep(0.5)
    tn2.write(b"\r\nenable\r\nCisco123!\r\nterminal length 0\r\n")
    time.sleep(0.5)
    tn2.read_very_eager()

    tn2.write(b"show spanning-tree brief\r\n")
    time.sleep(1)
    print(tn2.read_very_eager().decode('ascii', errors='ignore'))

    tn2.write(b"show port-security interface gi0/1\r\n")
    time.sleep(1)
    print(tn2.read_very_eager().decode('ascii', errors='ignore'))

    tn2.write(b"show mac address-table\r\n")
    time.sleep(1)
    print(tn2.read_very_eager().decode('ascii', errors='ignore'))
    tn2.close()

if __name__ == "__main__":
    check()

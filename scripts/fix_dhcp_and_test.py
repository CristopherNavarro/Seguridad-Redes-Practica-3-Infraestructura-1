import telnetlib
import time

HOST = "192.168.6.129"

def fix_and_test():
    # 1. Fix DHCP VCI match on FortiGate
    print("[*] Deshabilitando vci-match en DHCP servers de FortiGate...")
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

    cmds = [
        "config system dhcp server",
        "edit 1",
        "set vci-match disable",
        "next",
        "edit 2",
        "set vci-match disable",
        "next",
        "end"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r")
        time.sleep(0.1)

    time.sleep(1)
    tn.write(b"execute ping-options source 10.25.9.1\r")
    time.sleep(0.5)
    tn.write(b"execute ping 10.25.9.2\r")
    time.sleep(2)
    ping_dmz = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Ping FortiGate -> Srv-Web-Caja:\n", ping_dmz)
    tn.close()

    # 2. Trigger DHCP on PC1 and PC2
    for name, port in [("PC1-VLAN10", 5012), ("PC2-VLAN20", 5014)]:
        print(f"[*] Solicitando DHCP en {name} (puerto {port})...")
        tn_c = telnetlib.Telnet(HOST, port, timeout=5)
        time.sleep(0.5)
        tn_c.write(b"\r\nkillall udhcpc\r\nudhcpc -i eth0 -n -q -t 5\r\n")
        time.sleep(3)
        out = tn_c.read_very_eager().decode('ascii', errors='ignore')
        print(f"DHCP {name}:\n", out)
        tn_c.write(b"ip -4 addr show eth0; ip route\r\n")
        time.sleep(1)
        print(f"IP/Route {name}:\n", tn_c.read_very_eager().decode('ascii', errors='ignore'))
        tn_c.close()

if __name__ == "__main__":
    fix_and_test()

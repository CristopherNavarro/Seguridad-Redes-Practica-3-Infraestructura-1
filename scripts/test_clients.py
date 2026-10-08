import telnetlib
import time

HOST = "192.168.6.129"

def renew_dhcp(name, port):
    print(f"\n[*] Renovando DHCP en {name} (puerto {port})...")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    tn.write(b"killall udhcpc\r\n")
    time.sleep(0.5)
    tn.write(b"udhcpc -i eth0 -n -q -t 5\r\n")
    time.sleep(3)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("DHCP Output:\n", out)
    
    tn.write(b"ip -4 addr show eth0\r\n")
    time.sleep(1)
    ip_out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("IP Addr:\n", ip_out)
    tn.close()

if __name__ == "__main__":
    renew_dhcp("PC1-VLAN10", 5012)
    renew_dhcp("PC2-VLAN20", 5014)

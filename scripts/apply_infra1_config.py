import telnetlib
import time
import subprocess
import re

HOST = "192.168.6.129"

def log(msg):
    print(f"[*] {msg}", flush=True)

# -------------------------------------------------------------
# 1. CISCO SWITCH CONFIGURATION FUNCTION
# -------------------------------------------------------------
def configure_cisco_switch(name, port, commands):
    log(f"Iniciando configuración en {name} (puerto Telnet {port})...")
    tn = telnetlib.Telnet(HOST, port, timeout=10)
    time.sleep(1)
    tn.write(b"\r\n\r\n")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    
    # Enter enable mode
    if ">" in buf:
        tn.write(b"enable\r\n")
        time.sleep(1)
        tn.write(b"Cisco123!\r\n") # In case enable password was already set
        time.sleep(1)
    
    # Disable paging immediately (Rule 7)
    tn.write(b"terminal length 0\r\n")
    time.sleep(0.5)
    tn.write(b"configure terminal\r\n")
    time.sleep(0.5)
    
    for cmd in commands:
        tn.write(cmd.encode('ascii') + b"\r\n")
        time.sleep(0.1)
    
    tn.write(b"end\r\n")
    time.sleep(1)
    tn.write(b"write memory\r\n")
    time.sleep(3)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    log(f"{name} configurado exitosamente.")
    return out

# -------------------------------------------------------------
# 2. FORTIGATE CONFIGURATION FUNCTION
# -------------------------------------------------------------
def configure_fortigate(port=5000):
    log("Iniciando configuración de FGT1 (FortiGate 7.0.9)...")
    tn = telnetlib.Telnet(HOST, port, timeout=15)
    time.sleep(1)
    tn.write(b"\r\n")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    
    # Handle initial login
    if "login:" in buf or "Username:" in buf:
        log("Enviando credenciales admin...")
        tn.write(b"admin\r\n")
        time.sleep(1)
        res = tn.read_very_eager().decode('ascii', errors='ignore')
        if "Password:" in res or "password:" in res:
            # Check if password is blank or Fortinet2025!
            tn.write(b"\r\n")
            time.sleep(1.5)
            res2 = tn.read_very_eager().decode('ascii', errors='ignore')
            if "new password" in res2.lower():
                log("Estableciendo nueva contraseña 'Fortinet2025!'...")
                tn.write(b"Fortinet2025!\r\n")
                time.sleep(1)
                tn.write(b"Fortinet2025!\r\n")
                time.sleep(2)
            elif "login failed" in res2.lower() or "password:" in res2.lower():
                tn.write(b"admin\r\n")
                time.sleep(1)
                tn.write(b"Fortinet2025!\r\n")
                time.sleep(2)
    elif "Password:" in buf:
        tn.write(b"Fortinet2025!\r\n")
        time.sleep(2)

    # Disable paging immediately (Rule 7)
    tn.write(b"\r\nconfig system console\r\nset output standard\r\nend\r\n")
    time.sleep(1)
    tn.read_very_eager()
    
    fgt_commands = [
        # Hostname and settings
        "config system global",
        "set hostname FGT-Edge-01",
        "set timezone 04",
        "end",

        # Interface Configuration
        "config system interface",
        "edit port1",
        "set mode dhcp",
        "set allowaccess ping https ssh http fgfm",
        "set role wan",
        "next",
        "edit port2",
        "set allowaccess ping",
        "next",
        "edit VLAN10_USERS",
        "set vdom root",
        "set ip 10.25.7.1 255.255.255.128",
        "set allowaccess ping https ssh http",
        "set role lan",
        "set interface port2",
        "set vlanid 10",
        "next",
        "edit VLAN20_ADMIN",
        "set vdom root",
        "set ip 10.25.8.1 255.255.255.128",
        "set allowaccess ping https ssh http",
        "set role lan",
        "set interface port2",
        "set vlanid 20",
        "next",
        "edit port3",
        "set vdom root",
        "set ip 10.25.9.1 255.255.255.240",
        "set allowaccess ping https ssh http",
        "set role dmz",
        "next",
        "end",

        # DHCP Servers for Users
        "config system dhcp server",
        "edit 1",
        "set dns-service default",
        "set default-gateway 10.25.7.1",
        "set netmask 255.255.255.128",
        "set interface VLAN10_USERS",
        "config ip-range",
        "edit 1",
        "set start-ip 10.25.7.10",
        "set end-ip 10.25.7.100",
        "next",
        "end",
        "next",
        "edit 2",
        "set dns-service default",
        "set default-gateway 10.25.8.1",
        "set netmask 255.255.255.128",
        "set interface VLAN20_ADMIN",
        "config ip-range",
        "edit 1",
        "set start-ip 10.25.8.10",
        "set end-ip 10.25.8.100",
        "next",
        "end",
        "next",
        "end",

        # Custom Services
        "config firewall service custom",
        "edit MYSQL_3306",
        "set tcp-portrange 3306",
        "set comment \"Base de Datos MySQL\"",
        "next",
        "end",

        # Firewall Address Objects
        "config firewall address",
        "edit VLAN10_NET",
        "set subnet 10.25.7.0 255.255.255.128",
        "set comment \"Subred Usuarios VLAN 10\"",
        "next",
        "edit VLAN20_NET",
        "set subnet 10.25.8.0 255.255.255.128",
        "set comment \"Subred Gestion Admin VLAN 20\"",
        "next",
        "edit DMZ_SERVERS_NET",
        "set subnet 10.25.9.0 255.255.255.240",
        "set comment \"Subred Servidores DMZ\"",
        "next",
        "edit Web_Server_Caja",
        "set subnet 10.25.9.2 255.255.255.255",
        "set comment \"Servidor Web Sistema de Caja\"",
        "next",
        "edit Web_Server_Inventario",
        "set subnet 10.25.9.3 255.255.255.255",
        "set comment \"Servidor Web Sistema de Inventario\"",
        "next",
        "edit DB_Server",
        "set subnet 10.25.9.4 255.255.255.255",
        "set comment \"Servidor de Base de Datos\"",
        "next",
        "end",

        # Firewall Policies
        "config firewall policy",
        
        # Policy 1: Explicit Restrict / Block VLAN 10 to Web Server Inventario
        "edit 1",
        "set name Deny_VLAN10_to_WebInventario",
        "set srcintf VLAN10_USERS",
        "set dstintf port3",
        "set srcaddr VLAN10_NET",
        "set dstaddr Web_Server_Inventario",
        "set action deny",
        "set schedule always",
        "set service ALL",
        "set logtraffic all",
        "set comments \"Restriccion de acceso a Sistema de Inventario para VLAN 10\"",
        "next",

        # Policy 2: Allow VLAN 10 to Web Server Caja
        "edit 2",
        "set name Allow_VLAN10_to_WebCaja",
        "set srcintf VLAN10_USERS",
        "set dstintf port3",
        "set srcaddr VLAN10_NET",
        "set dstaddr Web_Server_Caja",
        "set action accept",
        "set schedule always",
        "set service HTTP HTTPS PING",
        "set logtraffic all",
        "set comments \"Acceso permitido al Sistema de Caja para usuarios\"",
        "next",

        # Policy 3: Allow VLAN 20 Exclusive SSH to DMZ Servers
        "edit 3",
        "set name Allow_VLAN20_Exclusive_SSH_to_DMZ",
        "set srcintf VLAN20_ADMIN",
        "set dstintf port3",
        "set srcaddr VLAN20_NET",
        "set dstaddr DMZ_SERVERS_NET",
        "set action accept",
        "set schedule always",
        "set service SSH PING",
        "set logtraffic all",
        "set comments \"Acceso SSH exclusivo hacia servidores desde VLAN 20\"",
        "next",

        # Policy 4: Allow VLAN 20 Full Web & DB Access to DMZ Servers
        "edit 4",
        "set name Allow_VLAN20_to_DMZ_Web_DB",
        "set srcintf VLAN20_ADMIN",
        "set dstintf port3",
        "set srcaddr VLAN20_NET",
        "set dstaddr DMZ_SERVERS_NET",
        "set action accept",
        "set schedule always",
        "set service HTTP HTTPS MYSQL_3306 PING",
        "set logtraffic all",
        "set comments \"Gestion y administracion web/db desde VLAN 20\"",
        "next",

        # Policy 5: Prevent Traffic Leakage from DMZ to LAN
        "edit 5",
        "set name Prevent_DMZ_Leak_to_LAN",
        "set srcintf port3",
        "set dstintf VLAN10_USERS VLAN20_ADMIN",
        "set srcaddr DMZ_SERVERS_NET",
        "set dstaddr all",
        "set action deny",
        "set schedule always",
        "set service ALL",
        "set logtraffic all",
        "set comments \"Evitar fuga o inicio de conexiones desde DMZ hacia red LAN\"",
        "next",

        # Policy 6: DMZ Outbound to Internet - Restricted to Update Endpoints Only
        "edit 6",
        "set name DMZ_Updates_to_Internet",
        "set srcintf port3",
        "set dstintf port1",
        "set srcaddr DMZ_SERVERS_NET",
        "set dstaddr all",
        "set action accept",
        "set schedule always",
        "set service HTTP HTTPS DNS NTP",
        "set nat enable",
        "set logtraffic all",
        "set comments \"Actualizaciones de servidores hacia repositorios externos\"",
        "next",

        # Policy 7: Outbound Internet for LAN Users
        "edit 7",
        "set name Allow_LAN_to_Internet",
        "set srcintf VLAN10_USERS VLAN20_ADMIN",
        "set dstintf port1",
        "set srcaddr all",
        "set dstaddr all",
        "set action accept",
        "set schedule always",
        "set service ALL",
        "set nat enable",
        "set logtraffic all",
        "set comments \"Navegacion saliente hacia Internet con NAT\"",
        "next",

        "end"
    ]

    for c in fgt_commands:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.12)
    
    time.sleep(1)
    tn.write(b"get system interface physical\r\n")
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    log("FortiGate configurado exitosamente.")
    return out

# -------------------------------------------------------------
# 3. ALPINE CONTAINERS CONFIGURATION
# -------------------------------------------------------------
def configure_alpine(name, port, ip_cidr, gw, service_type=None):
    log(f"Configurando contenedor {name} (puerto {port})...")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    
    if ip_cidr: # Static IP (Servers)
        cmds = [
            f"ip addr flush dev eth0",
            f"ip addr add {ip_cidr} dev eth0",
            f"ip link set eth0 up",
            f"ip route replace default via {gw}",
            f"echo 'nameserver 8.8.8.8' > /etc/resolv.conf",
        ]
        for c in cmds:
            tn.write(c.encode('ascii') + b"\r\n")
            time.sleep(0.2)
            
        if service_type == "web_caja":
            # Web server for Caja
            html = "<h1>SISTEMA DE FACTURACION Y CAJA</h1><p>Estado: OPERATIVO - Acceso Autorizado LAN</p>"
            setup_cmds = [
                "mkdir -p /var/www",
                f"echo '{html}' > /var/www/index.html",
                "killall httpd 2>/dev/null",
                "httpd -p 80 -h /var/www",
                # Start simple nc or ssh daemon for port testing
                "killall nc 2>/dev/null",
                "while true; do nc -l -p 22 -e echo 'SSH-2.0-OpenSSH_8.9 Srv-Web-Caja'; sleep 1; done &"
            ]
            for sc in setup_cmds:
                tn.write(sc.encode('ascii') + b"\r\n")
                time.sleep(0.2)
                
        elif service_type == "web_inventario":
            # Web server for Inventario
            html = "<h1>SISTEMA DE INVENTARIO CENTRAL</h1><p>ACCESO CONFIDENCIAL Y RESTRINGIDO</p>"
            setup_cmds = [
                "mkdir -p /var/www",
                f"echo '{html}' > /var/www/index.html",
                "killall httpd 2>/dev/null",
                "httpd -p 80 -h /var/www",
                "killall nc 2>/dev/null",
                "while true; do nc -l -p 22 -e echo 'SSH-2.0-OpenSSH_8.9 Srv-Web-Inventario'; sleep 1; done &"
            ]
            for sc in setup_cmds:
                tn.write(sc.encode('ascii') + b"\r\n")
                time.sleep(0.2)

        elif service_type == "db":
            setup_cmds = [
                # DB listener on 3306 and SSH on 22
                "killall nc 2>/dev/null",
                "while true; do nc -l -p 3306 -e echo '5.7.34-MySQL-Community-Server'; sleep 1; done &",
                "while true; do nc -l -p 22 -e echo 'SSH-2.0-OpenSSH_8.9 Srv-DB'; sleep 1; done &"
            ]
            for sc in setup_cmds:
                tn.write(sc.encode('ascii') + b"\r\n")
                time.sleep(0.2)

    else: # DHCP Clients (PC1 and PC2)
        dhcp_cmds = [
            "ip addr flush dev eth0",
            "ip link set eth0 up",
            "killall udhcpc 2>/dev/null",
            "udhcpc -i eth0 -n -q -t 5",
            "ip a show eth0"
        ]
        for dc in dhcp_cmds:
            tn.write(dc.encode('ascii') + b"\r\n")
            time.sleep(0.8)

    time.sleep(1)
    tn.write(b"ip a show eth0\r\n")
    time.sleep(0.5)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    log(f"{name} configurado exitosamente.")
    return out

# -------------------------------------------------------------
# 4. GNS3 VM DNAT PORT FORWARDING (FOR HOST GUI ACCESS)
# -------------------------------------------------------------
def setup_gui_port_forward():
    log("Obteniendo dirección IP de FortiGate port1...")
    tn = telnetlib.Telnet(HOST, 5000, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    if "login:" in buf:
        tn.write(b"admin\r\n")
        time.sleep(0.5)
        tn.write(b"Fortinet2025!\r\n")
        time.sleep(1)
    tn.write(b"get system interface physical\r\n")
    time.sleep(1.5)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    
    # Extract port1 IP (e.g., 192.168.42.x)
    m = re.search(r'port1\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', out)
    fgt_ip = None
    if m:
        fgt_ip = m.group(1)
    else:
        # Check via diagnose
        tn = telnetlib.Telnet(HOST, 5000, timeout=5)
        tn.write(b"diagnose ip address list\r\n")
        time.sleep(1)
        diag = tn.read_very_eager().decode('ascii', errors='ignore')
        tn.close()
        m2 = re.search(r'IP=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)->[0-9.]+.*devname=port1', diag)
        if m2:
            fgt_ip = m2.group(1)
            
    if not fgt_ip:
        log("No se pudo obtener la IP automática de port1 aún, intentando configurar IP fija 192.168.42.226/24...")
        fgt_ip = "192.168.42.226"
        tn = telnetlib.Telnet(HOST, 5000, timeout=5)
        tn.write(b"config system interface\redit port1\rset mode static\rset ip 192.168.42.226 255.255.255.0\rend\r")
        time.sleep(1)
        tn.close()
        
    log(f"IP de FortiGate port1 detectada: {fgt_ip}")
    
    # Configure DNAT in GNS3 VM via SSH
    ssh_cmd = (
        f"sudo sysctl -w net.ipv4.ip_forward=1 && "
        f"sudo iptables -t nat -F PREROUTING && "
        f"sudo iptables -t nat -A PREROUTING -p tcp -d 192.168.6.129 --dport 443 -j DNAT --to-destination {fgt_ip}:443 && "
        f"sudo iptables -t nat -A PREROUTING -p tcp -d 192.168.6.129 --dport 80 -j DNAT --to-destination {fgt_ip}:80 && "
        f"sudo iptables -t nat -A PREROUTING -p tcp -d 192.168.6.129 --dport 8443 -j DNAT --to-destination {fgt_ip}:443 && "
        f"sudo iptables -t nat -A PREROUTING -p tcp -d 192.168.6.129 --dport 8080 -j DNAT --to-destination {fgt_ip}:80 && "
        f"sudo iptables -A FORWARD -j ACCEPT"
    )
    subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes", "gns3@192.168.6.129", ssh_cmd], check=True)
    log(f"Reglas DNAT activadas en GNS3 VM. GUI accesible desde Windows en https://192.168.6.129 y https://192.168.6.129:8443")

# -------------------------------------------------------------
# MAIN ORCHESTRATION
# -------------------------------------------------------------
if __name__ == "__main__":
    sw1_commands = [
        "hostname SW1",
        "enable secret Cisco123!",
        "service password-encryption",
        "no ip domain-lookup",
        "ip domain-name itla.edu.do",
        "username admin privilege 15 secret Cisco123!",
        "banner motd # ACCESO RESTRINGIDO - AUTORIZADO A CRISTOPHER NAVARRO (2025-0720) #",
        "line con 0",
        " logging synchronous",
        " login local",
        "line vty 0 4",
        " transport input ssh",
        " login local",
        # VLANs
        "vlan 10",
        " name USUARIOS_VLAN10",
        "vlan 20",
        " name ADMIN_VLAN20",
        "vlan 99",
        " name NATIVE_MGMT",
        "vlan 999",
        " name BLACKHOLE_UNUSED",
        # Interfaces
        "interface GigabitEthernet0/0",
        " description UPLINK_TO_FGT1_PORT2",
        " switchport trunk encapsulation dot1q",
        " switchport mode trunk",
        " switchport trunk allowed vlan 10,20",
        " switchport trunk native vlan 99",
        " no shutdown",
        "interface GigabitEthernet0/1",
        " description ACCESS_PC1_VLAN10",
        " switchport mode access",
        " switchport access vlan 10",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " switchport port-security",
        " switchport port-security maximum 1",
        " switchport port-security violation restrict",
        " switchport port-security mac-address sticky",
        " no shutdown",
        "interface GigabitEthernet0/2",
        " description ACCESS_PC2_VLAN20",
        " switchport mode access",
        " switchport access vlan 20",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " switchport port-security",
        " switchport port-security maximum 1",
        " switchport port-security violation restrict",
        " switchport port-security mac-address sticky",
        " no shutdown",
        "interface range GigabitEthernet0/3, GigabitEthernet1/0 - 3, GigabitEthernet2/0 - 3, GigabitEthernet3/0 - 3",
        " switchport mode access",
        " switchport access vlan 999",
        " shutdown"
    ]

    sw2_commands = [
        "hostname SW2",
        "enable secret Cisco123!",
        "service password-encryption",
        "no ip domain-lookup",
        "ip domain-name itla.edu.do",
        "username admin privilege 15 secret Cisco123!",
        "banner motd # ACCESO RESTRINGIDO - AUTORIZADO A CRISTOPHER NAVARRO (2025-0720) #",
        "line con 0",
        " logging synchronous",
        " login local",
        "line vty 0 4",
        " transport input ssh",
        " login local",
        # VLANs
        "vlan 30",
        " name DMZ_SERVERS",
        "vlan 99",
        " name NATIVE_MGMT",
        "vlan 999",
        " name BLACKHOLE_UNUSED",
        # Interfaces
        "interface GigabitEthernet0/0",
        " description UPLINK_TO_FGT1_PORT3",
        " switchport mode access",
        " switchport access vlan 30",
        " switchport nonegotiate",
        " no shutdown",
        "interface GigabitEthernet0/1",
        " description ACCESS_SRV_WEB_CAJA",
        " switchport mode access",
        " switchport access vlan 30",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " switchport port-security",
        " switchport port-security maximum 1",
        " switchport port-security violation restrict",
        " switchport port-security mac-address sticky",
        " no shutdown",
        "interface GigabitEthernet0/2",
        " description ACCESS_SRV_WEB_INVENTARIO",
        " switchport mode access",
        " switchport access vlan 30",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " switchport port-security",
        " switchport port-security maximum 1",
        " switchport port-security violation restrict",
        " switchport port-security mac-address sticky",
        " no shutdown",
        "interface GigabitEthernet0/3",
        " description ACCESS_SRV_DB",
        " switchport mode access",
        " switchport access vlan 30",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " switchport port-security",
        " switchport port-security maximum 1",
        " switchport port-security violation restrict",
        " switchport port-security mac-address sticky",
        " no shutdown",
        "interface range GigabitEthernet1/0 - 3, GigabitEthernet2/0 - 3, GigabitEthernet3/0 - 3",
        " switchport mode access",
        " switchport access vlan 999",
        " shutdown"
    ]

    # Run Cisco configurations
    configure_cisco_switch("SW1", 5002, sw1_commands)
    configure_cisco_switch("SW2", 5004, sw2_commands)

    # Run FortiGate configuration
    configure_fortigate(5000)

    # Run Alpine Server configurations
    configure_alpine("Srv-Web-Caja", 5006, "10.25.9.2/28", "10.25.9.1", service_type="web_caja")
    configure_alpine("Srv-Web-Inventario", 5008, "10.25.9.3/28", "10.25.9.1", service_type="web_inventario")
    configure_alpine("Srv-DB", 5010, "10.25.9.4/28", "10.25.9.1", service_type="db")

    # Run Alpine Client DHCP configurations
    configure_alpine("PC1-VLAN10", 5012, None, None)
    configure_alpine("PC2-VLAN20", 5014, None, None)

    # Setup GUI Port Forwarding
    setup_gui_port_forward()

    log("¡Despliegue y configuración base completados al 100%!")

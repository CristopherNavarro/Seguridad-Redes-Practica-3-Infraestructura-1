import telnetlib
import time
import subprocess
import re

HOST = "192.168.6.129"
PORT = 5000

def log(msg):
    print(f"[*] {msg}", flush=True)

def connect_fgt():
    tn = telnetlib.Telnet(HOST, PORT, timeout=10)
    time.sleep(1)
    tn.write(b"\x03\r\x03\r")
    time.sleep(1)
    tn.write(b"\r")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    
    if "login:" in buf.lower():
        log("Logging in with admin...")
        tn.write(b"admin\r")
        time.sleep(1)
        res = tn.read_very_eager().decode('ascii', errors='ignore')
        if "password:" in res.lower():
            log("Sending password Fortinet2025!...")
            tn.write(b"Fortinet2025!\r")
            time.sleep(1.5)
    elif "password:" in buf.lower():
        log("Sending password Fortinet2025!...")
        tn.write(b"Fortinet2025!\r")
        time.sleep(1.5)
        
    # Disable paging immediately
    tn.write(b"config system console\rset output standard\rend\r")
    time.sleep(1)
    tn.read_very_eager()
    return tn

def apply_configuration():
    tn = connect_fgt()
    log("Aplicando configuraciones completas a FortiGate...")

    cmds = [
        # 1. System Global
        "config system global",
        "set hostname FGT-Edge-01",
        "set timezone 04",
        "end",

        # 2. Interfaces
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

        # 3. DHCP Servers
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

        # 4. Custom Services
        "config firewall service custom",
        "edit MYSQL_3306",
        "set tcp-portrange 3306",
        "set comment \"Base de Datos MySQL\"",
        "next",
        "end",

        # 5. Address Objects
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

        # 6. Firewall Policies
        "config firewall policy",
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
        "set comments \"Restriccion de acceso a Inventario para VLAN 10\"",
        "next",
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
        "set comments \"Acceso autorizado a Caja desde VLAN 10\"",
        "next",
        "edit 3",
        "set name Allow_VLAN20_SSH_to_DMZ",
        "set srcintf VLAN20_ADMIN",
        "set dstintf port3",
        "set srcaddr VLAN20_NET",
        "set dstaddr DMZ_SERVERS_NET",
        "set action accept",
        "set schedule always",
        "set service SSH PING",
        "set logtraffic all",
        "set comments \"Acceso SSH exclusivo a DMZ desde VLAN 20\"",
        "next",
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
        "set comments \"Acceso administrativo web y db desde VLAN 20\"",
        "next",
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
        "set comments \"Prevencion de fuga de conexiones DMZ hacia LAN\"",
        "next",
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
        "set comments \"Permitir actualizaciones de repositorios desde DMZ\"",
        "next",
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
        "set comments \"Salida a Internet para usuarios LAN\"",
        "next",
        "end"
    ]

    for c in cmds:
        tn.write(c.encode('ascii') + b"\r")
        time.sleep(0.12)
        
    time.sleep(1)
    tn.write(b"show system interface\r")
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Interface Config Output Snippet:\n", out[:500])
    
    tn.write(b"show firewall policy\r")
    time.sleep(1)
    policies_out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Policy Config Output:\n", policies_out)
    tn.close()
    log("[+] FortiGate configurado al 100%!")

if __name__ == "__main__":
    apply_configuration()

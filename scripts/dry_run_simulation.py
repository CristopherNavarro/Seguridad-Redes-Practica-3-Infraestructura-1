import telnetlib
import time
import requests
import os

HOST = "192.168.6.129"
OUTPUT_FILE = r"c:\Users\crist\Downloads\Tareas Seguridad de Redes (GNS3)\Archivos para mi\bitacora_ensayo_infraestructura_1.txt"

def exec_session(name, port, commands, is_cisco=False):
    log_lines = [f"\n{'='*30} [{name} - Puerto {port}] {'='*30}\n"]
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    
    if is_cisco:
        if ">" in buf:
            tn.write(b"enable\r\nCisco123!\r\n")
            time.sleep(0.5)
        tn.write(b"terminal length 0\r\n")
        time.sleep(0.3)
        tn.read_very_eager()
        
    for cmd in commands:
        log_lines.append(f">>> {cmd}\n")
        tn.write(cmd.encode('ascii') + b"\r\n")
        time.sleep(1)
        res = tn.read_very_eager().decode('ascii', errors='ignore')
        log_lines.append(res + "\n")
        
    tn.close()
    return "".join(log_lines)

def run_dry_run():
    full_log = []
    full_log.append("======================================================================\n")
    full_log.append("   SIMULACRO EN VIVO (DRY RUN) - ENSAYO CRONOLOGICO PARA GRABACION    \n")
    full_log.append("   Estudiante: Cristopher Navarro (2025-0720)                         \n")
    full_log.append("   Asignatura: Seguridad de Redes | Docente: Jonathan Rondon          \n")
    full_log.append("======================================================================\n\n")

    # 1. FortiGate GUI Test
    full_log.append("[BLOQUE 1: VERIFICACION DE PORTAL FORTIGATE GUI]\n")
    try:
        r = requests.get("http://192.168.6.129:8080", timeout=5)
        full_log.append(f"HTTP GET http://192.168.6.129:8080 -> Status Code: {r.status_code} (OK - Portal Disponible)\n")
    except Exception as e:
        full_log.append(f"Error accediendo GUI: {e}\n")

    # 2. Cisco SW1
    sw1_cmds = [
        "show vlan brief",
        "show interfaces trunk",
        "show port-security interface gi0/1",
        "show port-security interface gi0/2"
    ]
    full_log.append(exec_session("SW1 (Cisco IOSvL2 - LAN)", 5002, sw1_cmds, is_cisco=True))

    # 3. Cisco SW2
    sw2_cmds = [
        "show vlan brief",
        "show port-security interface gi0/1",
        "show interfaces status"
    ]
    full_log.append(exec_session("SW2 (Cisco IOSvL2 - DMZ)", 5004, sw2_cmds, is_cisco=True))

    # 4. PC1-VLAN10 (Usuario Estándar)
    pc1_cmds = [
        "ip -4 addr show eth0",
        "ping -c 2 10.25.7.1",
        "wget -T 3 -q -O - http://10.25.9.2",
        "wget -T 3 -q -O - http://10.25.9.3 || echo 'BLOQUEADO_POR_POLITICA_1'",
        "nc -w 2 10.25.9.2 22 || echo 'SSH_DENEGADO_A_VLAN10'"
    ]
    full_log.append(exec_session("PC1-VLAN10 (Usuario Estándar)", 5012, pc1_cmds))

    # 5. PC2-VLAN20 (Usuario Administrador)
    pc2_cmds = [
        "ip -4 addr show eth0",
        "ping -c 2 10.25.8.1",
        "nc -w 2 10.25.9.2 22",
        "nc -w 2 10.25.9.3 22",
        "nc -w 2 10.25.9.4 22",
        "wget -T 3 -q -O - http://10.25.9.3"
    ]
    full_log.append(exec_session("PC2-VLAN20 (Usuario Administrador)", 5014, pc2_cmds))

    # 6. Srv-Web-Caja (Anti-Leak DMZ -> LAN)
    srv_cmds = [
        "ip -4 addr show eth0",
        "ping -c 2 -W 2 10.25.7.10 || echo 'FUGA_DE_TRAFICO_BLOQUEADA_EXITOSAMENTE'"
    ]
    full_log.append(exec_session("Srv-Web-Caja (Servidor DMZ)", 5006, srv_cmds))

    full_output = "".join(full_log)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_output)
        
    print(f"[+] Ensayo general completado. Resultados guardados en:\n    {OUTPUT_FILE}")
    print("\nResumen de ejecución del simulacro:")
    print("----------------------------------------------------------------------")
    for block in full_output.split("="*30):
        if block.strip():
            lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
            if lines:
                print(f"[*] {lines[0]}: {len(lines)} lineas registradas.")

if __name__ == "__main__":
    run_dry_run()

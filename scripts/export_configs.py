import telnetlib
import time
import shutil
import os

HOST = "192.168.6.129"
CONFIG_DIR = r"c:\Users\crist\Downloads\Tareas Seguridad de Redes (GNS3)\Entregables para el profesor Github\configs"
os.makedirs(CONFIG_DIR, exist_ok=True)

def get_cisco_run(name, port):
    print(f"[*] Exportando running-config de {name}...")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\nterminal length 0\r\n")
    time.sleep(0.5)
    tn.read_very_eager()
    tn.write(b"show running-config\r\n")
    time.sleep(3)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    
    # Clean output
    filepath = os.path.join(CONFIG_DIR, f"{name}_running_config.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[+] {name} guardado en {filepath}")

def get_fgt_config():
    print("[*] Exportando configuracion de FortiGate...")
    tn = telnetlib.Telnet(HOST, 5000, timeout=10)
    time.sleep(0.5)
    tn.write(b"\r\n")
    time.sleep(0.5)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    if "login:" in buf.lower():
        tn.write(b"admin\rFortinet2025!\r")
        time.sleep(1)
    tn.write(b"config system console\rset output standard\rend\r")
    time.sleep(0.5)
    tn.read_very_eager()
    tn.write(b"show\r")
    time.sleep(4)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    
    filepath = os.path.join(CONFIG_DIR, "FortiGate_running_config.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[+] FortiGate guardado en {filepath}")

def copy_gns3_project():
    src = r"C:\Users\crist\GNS3\projects\9f30f078-3d55-4b65-88dd-01a6fd4dfb30\Seguridad_Redes_P3_Infraestructura_1.gns3"
    dst = r"c:\Users\crist\Downloads\Tareas Seguridad de Redes (GNS3)\Entregables para el profesor Github\Seguridad_Redes_P3_Infraestructura_1.gns3"
    shutil.copy2(src, dst)
    print(f"[+] Respaldo de topología GNS3 copiado a {dst}")

if __name__ == "__main__":
    get_cisco_run("SW1", 5002)
    get_cisco_run("SW2", 5004)
    get_fgt_config()
    copy_gns3_project()

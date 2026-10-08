import paramiko

def check_gns3_vm():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect("192.168.6.129", username="gns3", password="gns3", timeout=5)
        stdin, stdout, stderr = ssh.exec_command("ip a; sudo iptables -t nat -L -n -v")
        print("=== GNS3 VM Interfaces & NAT ===")
        print(stdout.read().decode())
        ssh.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_gns3_vm()

import paramiko

USERNAME = 'cisco'
KEY_PATH = 'private_key.key'

devices_ip = [
    "172.31.67.1",   # R0
    "172.31.67.4",   # R1
    "172.31.67.5",   # R2
    "172.31.67.2",   # S0
    "172.31.67.3",   # S1
]

private_key = paramiko.RSAKey.from_private_key_file(KEY_PATH)

for ip in devices_ip:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"(Public-key) Connecting to {ip}")
    client.connect(
        hostname=ip,
        username=USERNAME,
        pkey=private_key,
        disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]}
    )

    stdin, stdout, stderr = client.exec_command("show ip interface brief")
    print(stdout.read().decode())
    client.close()


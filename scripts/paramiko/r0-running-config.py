import paramiko

USERNAME = "cisco"
KEY_PATH = "private_key.key"

devices = {
    "172.31.67.1": "r0-running-config.log",
}

private_key = paramiko.RSAKey.from_private_key_file(KEY_PATH)

for ip, filename in devices.items():
    print(f"(Public-key) Connecting to {ip}")

    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=ip,
            username=USERNAME,
            pkey=private_key,
            disabled_algorithms={
                "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
            },
        )

        stdin, stdout, stderr = client.exec_command("show run")

        output = stdout.read().decode()

        with open(filename, "w") as f:
            f.write(output)

        stdin.close()
        stdout.close()
        stderr.close()

    print(f"Running configuration saved to {filename}")
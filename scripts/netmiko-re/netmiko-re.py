import re
from netmiko import ConnectHandler

USERNAME = 'cisco'
KEY_PATH = 'private_key.key'

DEVICES = {
    "R1": "172.31.67.4",
    "R2": "172.31.67.5",
}

# "GigabitEthernet0/1  10.0.67.4  YES NVRAM  up  up" -> ("GigabitEthernet0/1", "10.0.67.4")
ACTIVE_INTERFACE_RE = re.compile(
    r"^(\S+)\s+(\S+)\s+\S+\s+\S+\s+up\s+up\s*$",
    re.MULTILINE,
)

# "R1 uptime is 1 hour, 32 minutes" -> "1 hour, 32 minutes"
UPTIME_RE = re.compile(r"^\S+\s+uptime\s+is\s+(.+?)\s*$", re.MULTILINE)

for name, host in DEVICES.items():
    network_device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": USERNAME,
        "secret": "cisco",
        "use_keys": True,
        "key_file": KEY_PATH,
        "disabled_algorithms": {
            "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
        },
    }

    net_connect = ConnectHandler(**network_device)
    net_connect.enable()
    print(f"Connected to {name}")

    version_output = net_connect.send_command("show version")
    uptime_match = UPTIME_RE.search(version_output)
    uptime = uptime_match.group(1) if uptime_match else "unknown"

    brief_output = net_connect.send_command("show ip interface brief")
    active_interfaces = ACTIVE_INTERFACE_RE.findall(brief_output)

    net_connect.disconnect()

    print(f"[{name} ({host})]")
    print(f"Uptime: {uptime}")
    print("Active interfaces:")
    for interface, ip_address in active_interfaces:
        print(f"  {interface:<25} {ip_address}")
    print()

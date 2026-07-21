import re
import pprint
from pathlib import Path
from netmiko import ConnectHandler

USERNAME = "cisco"
SECRET = "cisco"
KEY_PATH = "private_key.key"

DEVICES = {
    "S1": "172.31.67.3",
    "R1": "172.31.67.4",
    "R2": "172.31.67.5",
}

MGMT_DEVICES = {"R0", "S0"}
MGMT_INTERFACES = {"GigabitEthernet0/0"}

STATIC_DESCRIPTIONS = {
    "R1": {},
    "R2": {
        "GigabitEthernet0/2": "Connect to PC",
        "GigabitEthernet0/3": "Connect to WAN",
    },
    "S1": {
        "GigabitEthernet1/1": "Connect to PC",
    },
}

INTERFACE_ABBREVIATIONS = [
    ("TenGigabitEthernet", "Te"),
    ("GigabitEthernet", "G"),
    ("FastEthernet", "F"),
    ("Ethernet", "E"),
    ("Port-channel", "Po"),
    ("Loopback", "Lo"),
]

INTERFACE_RE = re.compile(r"^([A-Za-z-]+)\s*(\S*)$")

def shorten_interface(name: str) -> str:
    """GigabitEthernet0/1 -> G0/1"""
    match = INTERFACE_RE.match(name.strip())
    if not match:
        return name.strip()
    prefix, number = match.groups()
    for long_name, short_name in INTERFACE_ABBREVIATIONS:
        if prefix.lower().startswith(long_name.lower()):
            return f"{short_name}{number}"
    return name.strip()


def strip_domain(hostname: str) -> str:
    """R2.kmitl.com -> R2"""
    return hostname.strip().split(".")[0]


def build_description_commands(device_name: str, neighbors) -> list[str]:
    """config commands from parsed CDP neighbors and static PC/WAN mapping"""
    static = STATIC_DESCRIPTIONS[device_name]
    commands = []

    if not isinstance(neighbors, list):
        print(f"{device_name} : CDP output was not parsed by TextFSM, "
              f"skip CDP descriptions")
        neighbors = []

    for neighbor in neighbors:
        local_intf = neighbor["local_interface"].strip()
        remote_intf = neighbor["neighbor_interface"].strip()
        remote_name = strip_domain(neighbor["neighbor_name"])

        # Skip management interfaces and devices
        if local_intf in MGMT_INTERFACES or remote_name in MGMT_DEVICES:
            continue

        # PC/WAN rule wins over any CDP entry
        if local_intf in static:
            continue

        description = f"Connect to {shorten_interface(remote_intf)} of {remote_name}"
        commands += [f"interface {local_intf}", f"description {description}"]

    for interface, description in static.items():
        commands += [f"interface {interface}", f"description {description}"]

    return commands


def configure_device(device_name: str, host: str) -> None:
    """Connect to one device apply CDP-derived and static descriptions close session"""
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": USERNAME,
        "secret": SECRET,
        "use_keys": True,
        "key_file": KEY_PATH,
        "disabled_algorithms": {
            "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
        },
    }

    ssh = ConnectHandler(**device)
    ssh.enable()
    print(f"{device_name} [{host}]")

    neighbors = ssh.send_command("show cdp neighbors detail", use_textfsm=True)
    print(f"{device_name} : parse CDP neighbors")
    pprint.pprint(neighbors)

    commands = build_description_commands(device_name, neighbors)
    print(f"{device_name} : config commands")
    print("\n".join(commands))
    ssh.send_config_set(commands)
    ssh.save_config()

    print(f"{device_name} : show interfaces description")
    print(ssh.send_command("show interfaces description"))

    ssh.disconnect()


configure_device("S1", DEVICES["S1"])
configure_device("R1", DEVICES["R1"])
configure_device("R2", DEVICES["R2"])

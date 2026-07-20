from jinja2 import Environment, FileSystemLoader
from scripts.netmiko.netmikolab import ConnectHandler
from pathlib import Path

USERNAME = 'cisco'
KEY_PATH = 'private_key.key'

DEVICES = {
    "R0": "172.31.67.1",
    "S0": "172.31.67.2",
    "S1": "172.31.67.3",
    "R1": "172.31.67.4",
    "R2": "172.31.67.5",
}

# Setup Jinja2 environment
template_dir = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(template_dir))

# Device-specific configuration data
S1_DATA = {
    "vlan_id": 101,
    "access_ports": ["g0/1", "g1/1"]
}

R1_DATA = {
    "remove_routes": [
        "no ip route vrf control-data 10.0.68.0 255.255.255.0 10.0.68.1",
        "no ip route vrf control-data 10.0.69.0 255.255.255.0 10.0.68.1",
    ],
    "vrf_name": "control-data",
    "loopback_ip": "10.0.0.1",
    "ospf_id": 1,
    "router_id": "10.0.0.1",
    "networks": [
        {"prefix": "10.0.0.1", "wildcard": "0.0.0.0", "area": 0},
        {"prefix": "10.0.67.0", "wildcard": "0.0.0.255", "area": 0},
        {"prefix": "10.0.68.0", "wildcard": "0.0.0.255", "area": 0},
    ],
    "access_lists": [
        {"number": 20, "subnet": "172.31.67.0", "wildcard": "0.0.0.15"},
        {"number": 20, "subnet": "10.200.118.0", "wildcard": "0.0.0.255"},
    ]
}

R2_DATA = {
    "remove_routes": [
        "no ip route vrf control-data 10.0.67.0 255.255.255.0 10.0.67.4",
        "no ip route vrf control-data 10.0.67.0 255.255.255.0 10.0.68.2",
    ],
    "vrf_name": "control-data",
    "loopback_ip": "10.0.0.2",
    "ospf_id": 1,
    "router_id": "10.0.0.2",
    "networks": [
        {"prefix": "10.0.0.2", "wildcard": "0.0.0.0", "area": 0},
        {"prefix": "10.0.68.0", "wildcard": "0.0.0.255", "area": 0},
        {"prefix": "10.0.69.0", "wildcard": "0.0.0.255", "area": 0},
    ],
    "nat_acls": [
        {"number": 10, "subnet": "10.0.67.0", "wildcard": "0.0.0.255"},
        {"number": 10, "subnet": "10.0.69.0", "wildcard": "0.0.0.255"},
    ],
    "nat_inside_list": 10,
    "access_lists": [
        {"number": 20, "subnet": "172.31.67.0", "wildcard": "0.0.0.15"},
        {"number": 20, "subnet": "10.200.118.0", "wildcard": "0.0.0.255"},
    ]
}

# Map devices to their templates and data
DEVICE_CONFIGS = {
    "S1": ("s1_vlan.j2", S1_DATA),
    "R1": ("r1_ospf.j2", R1_DATA),
    "R2": ("r2_ospf_nat.j2", R2_DATA),
}


def render_config(template_name: str, data: dict) -> list[str]:
    """Render Jinja2 template and return as list of commands."""
    template = env.get_template(template_name)
    rendered = template.render(data)
    # Parse rendered template into commands, filtering out empty lines and comments
    commands = [
        line.strip()
        for line in rendered.split('\n')
        if line.strip() and not line.strip().startswith('!')
    ]
    return commands


def main() -> None:
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

        # Apply configuration if device has a template
        if name in DEVICE_CONFIGS:
            template_name, config_data = DEVICE_CONFIGS[name]
            config_commands = render_config(template_name, config_data)
            net_connect.send_config_set(config_commands)
            print(f"[✓] Configuration applied to {name} using {template_name}")
        else:
            print(f"[i] No configuration template for {name}")

        # Show interface status
        output = net_connect.send_command("show ip int br")
        print(output)
        print()

        net_connect.disconnect()


if __name__ == "__main__":
    main()

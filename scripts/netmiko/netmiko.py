from netmiko import ConnectHandler

USERNAME = 'cisco'
KEY_PATH = 'private_key.key'

DEVICES = {
    "R0": "172.31.67.1",
    "S0": "172.31.67.2",
    "S1": "172.31.67.3",
    "R1": "172.31.67.4",
    "R2": "172.31.67.5",
}

VLAN101_CONF = [
    "vlan 101",
    "exit",
    "int g0/1",
    "switchport access vlan 101",
    "int g1/1",
    "switchport access vlan 101",
    "int vlan 101",
    "no shut",
]

R1_CONF = [
    "no ip route vrf control-data 10.0.68.0 255.255.255.0 10.0.68.1",
    "no ip route vrf control-data 10.0.69.0 255.255.255.0 10.0.68.1",

    "int lo0",
    "vrf forwarding control-data",
    "ip address 10.0.0.1 255.255.255.255",
    "no shut",

    "router ospf 1 vrf control-data",
    "router-id 10.0.0.1",
    "network 10.0.0.1 0.0.0.0 area 0",
    "network 10.0.67.0 0.0.0.255 area 0",
    "network 10.0.68.0 0.0.0.255 area 0",

    "access-list 20 permit 172.31.67.0 0.0.0.15",
    "access-list 20 permit 10.200.118.0 0.0.0.255",
    "line vty 0 4",
    "access-class 20 in",
]

R2_CONF = [
    "no ip route vrf control-data 10.0.67.0 255.255.255.0 10.0.67.4",
    "no ip route vrf control-data 10.0.67.0 255.255.255.0 10.0.68.2",

    "int lo0",
    "vrf forwarding control-data",
    "ip address 10.0.0.2 255.255.255.255",
    "no shut",

    "int g0/2",
    "no shutdown",

    "router ospf 1 vrf control-data",
    "router-id 10.0.0.2",
    "default-information originate always",
    "network 10.0.0.2 0.0.0.0 area 0",
    "network 10.0.68.0 0.0.0.255 area 0",
    "network 10.0.69.0 0.0.0.255 area 0",

    "int g0/3",
    "vrf forwarding control-data",
    "ip address dhcp",
    "no shutdown",
    "ip nat outside",

    "int range g0/1-2",
    "ip nat inside",

    "access-list 10 permit 10.0.67.0 0.0.0.255",
    "access-list 10 permit 10.0.69.0 0.0.0.255",
    "ip nat inside source list 10 interface g0/3 vrf control-data overload",

    "access-list 20 permit 172.31.67.0 0.0.0.15",
    "access-list 20 permit 10.200.118.0 0.0.0.255",
    "line vty 0 4",
    "access-class 20 in",
]

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

    net_connect = None
    net_connect = ConnectHandler(**network_device)
    net_connect.enable()
    print(f"Connected to {name}")

    if name == "S1":
        net_connect.send_config_set(VLAN101_CONF)
        print("conf vlan 101 on S1")
    elif name == "R1":
        net_connect.send_config_set(R1_CONF)
        print("conf r1 ospf")
    elif name == "R2":
        net_connect.send_config_set(R2_CONF)
        print("conf r2 ospf and nat")

    output = net_connect.send_command("show ip int br")
    print(output)

    net_connect.disconnect()
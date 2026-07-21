import pytest
from netmiko import ConnectHandler

USERNAME = "cisco"
SECRET = "cisco"
KEY_PATH = "private_key.key"

DEVICES = {
    "S1": "172.31.67.3",
    "R1": "172.31.67.4",
    "R2": "172.31.67.5",
}

def connect(device_name):
    """Open SSH session to the device, fetch, parse show interfaces description and close the session"""
    
    device = {
        "device_type": "cisco_ios",
        "host": DEVICES[device_name],
        "username": USERNAME,
        "secret": SECRET,
        "use_keys": True,
        "key_file": KEY_PATH,
        "disabled_algorithms": {
            "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"],
        },
    }
    
    conn = ConnectHandler(**device)
    conn.enable()
    rows = conn.send_command("show interfaces description", use_textfsm=True)

    assert isinstance(rows, list), (f"TextFSM did not parse output, got raw string: {rows!r}")
    
    descriptions = {row["port"]: row["description"] for row in rows}
    
    conn.disconnect()
    
    return descriptions


@pytest.fixture(scope="module")
def s1_descriptions():
    return connect("S1")


@pytest.fixture(scope="module")
def r1_descriptions():
    return connect("R1")


@pytest.fixture(scope="module")
def r2_descriptions():
    return connect("R2")


def assert_description(descriptions, interface, expected):
    assert interface in descriptions, (
        f"{interface} not found, interfaces seen: {sorted(descriptions)}"
    )
    assert descriptions[interface] == expected


class TestS1:
    def test_gi0_1(self, s1_descriptions):
        assert_description(s1_descriptions, "Gi0/1", "Connect to G0/2 of R2")

    def test_gi1_1(self, s1_descriptions):
        assert_description(s1_descriptions, "Gi1/1", "Connect to PC")


class TestR1:
    def test_gi0_1(self, r1_descriptions):
        assert_description(r1_descriptions, "Gi0/1", "Connect to G0/1 of PC")

    def test_gi0_2(self, r1_descriptions):
        assert_description(r1_descriptions, "Gi0/2", "Connect to G0/1 of R2")


class TestR2:
    def test_gi0_1(self, r2_descriptions):
        assert_description(r2_descriptions, "Gi0/1", "Connect to G0/2 of R1")

    def test_gi0_2(self, r2_descriptions):
        assert_description(r2_descriptions, "Gi0/2", "Connect to G0/1 of S1")

    def test_gi0_3(self, r2_descriptions):
        assert_description(r2_descriptions, "Gi0/3", "Connect to WAN")
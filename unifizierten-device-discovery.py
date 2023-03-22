import re
from scapy.all import ARP, Ether, srp

def find_unifi_devices(ip_range):
    # Send ARP requests to the specified IP range
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packets and capture the responses
    result = srp(packet, timeout=2, verbose=0)[0]

    # Process the responses
    unifi_devices = []
    for sent, received in result:
        mac_address = received.hwsrc
        ip_address = received.psrc

        # Check if the MAC address belongs to a UniFi device
        if is_unifi_mac(mac_address):
            unifi_device = {"ip": ip_address, "mac": mac_address}
            unifi_devices.append(unifi_device)

    return unifi_devices

def is_unifi_mac(mac):
    # UniFi MAC address prefixes
    unifi_mac_prefixes = [
        "04:18:d6", "44:d9:e7", "b4:fb:e4", "78:8a:20", "80:2a:a8", "e0:63:da", "f0:9f:c2"
    ]
    for prefix in unifi_mac_prefixes:
        if mac.lower().startswith(prefix):
            return True
    return False

if __name__ == "__main__":
    ip_range = "192.168.1.0/24"  # Adjust this to your network IP range
    unifi_devices = find_unifi_devices(ip_range)

    if unifi_devices:
        print("UniFi-Geräte gefunden:")
        for device in unifi_devices:
            print(f"IP: {device['ip']}, MAC: {device['mac']}")
    else:
        print("Keine UniFi-Geräte gefunden.")

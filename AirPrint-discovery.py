import socket
from zeroconf import ServiceBrowser, Zeroconf


class AirPrintListener:
    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            address = socket.inet_ntoa(info.address)
            port = info.port
            properties = info.properties
            printer_name = properties.get(b'ty', b'').decode('utf-8')
            print(f"Found AirPrint device: {printer_name}")
            print(f"  IP address: {address}")
            print(f"  Port: {port}")
            print(f"  Properties: {properties}")


def discover_airprint_devices():
    airprint_service = "_ipp._tcp.local."
    zeroconf = Zeroconf()
    listener = AirPrintListener()
    browser = ServiceBrowser(zeroconf, airprint_service, listener)

    try:
        input("Press Enter to stop browsing...\n")
    finally:
        zeroconf.close()


if __name__ == "__main__":
    discover_airprint_devices()

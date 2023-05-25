import os
import sys
import time
import struct
import socket
import select
import threading
import subprocess


ICMP_ECHO_REQUEST = 8  # ICMP ECHO REQUEST packet type
WATCHDOG_PORT = 3000
WATCHDOG_TIMEOUT = 10  # Timeout in seconds


def calculate_checksum(data):
    """Calculate the ICMP checksum."""
    checksum = 0
    count_to = (len(data) // 2) * 2

    for count in range(0, count_to, 2):
        checksum += (data[count + 1] << 8) + data[count]

    if count_to < len(data):
        checksum += data[len(data) - 1]

    checksum &= 0xFFFF
    return checksum


def send_ping_request(icmp_socket, dest_addr):
    """Send an ICMP ECHO REQUEST packet."""

    icmp_header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, 0, 1)
    checksum = calculate_checksum(icmp_header)
    icmp_header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, checksum, 0, 1)
    packet = icmp_header
    print("sending packets to {}".format(dest_addr))
    icmp_socket.sendto(packet, (dest_addr, 1))
    print("packets sent to {}".format(dest_addr))
    


def receive_ping_reply(icmp_socket, start_time):
    """Receive and process ICMP ECHO REPLY packets."""
    try:
        print("in try")
        
        received_packet, addr = icmp_socket.recvfrom(1024)
        print("still in try")
        time_elapsed = time.time() - start_time
        print("still in try")
        ip_header = received_packet[:20]
        ip_version, _, _, _, _, _ = struct.unpack('!BBHHHBBH4s4s', ip_header)
        print("still..... in try")
        icmp_header = received_packet[20:28]
        icmp_type, _, _, _, _ = struct.unpack('!BBHHH', icmp_header)
        print("STILLL in try")
        if icmp_type == ICMP_ECHO_REQUEST:
            print(f'Received packet from {addr[0]}: seq=1 time={int(time_elapsed * 1000)}ms')

            # Update the watchdog timer
            subprocess.call(['echo', 'reset', '|', 'nc', 'localhost', '3000'])

    except socket.timeout as e:
        print('Request timed out.')
        print(f'Exeption: {e}')


def ping(dest_addr):
    try:
        dest_ip = socket.gethostbyname(dest_addr)
        print(f'Pinging {dest_ip} with 32 bytes of data:')

        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_socket.settimeout(1)
        
        while True:
            print("in true")
            start_time = time.time()
            """Send an ICMP ECHO REQUEST packet."""

            icmp_header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, 0, 1)
            checksum = calculate_checksum(icmp_header)
            icmp_header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, checksum, 0, 1)
            packet = icmp_header
            print("sending packets to {}".format(dest_addr))
            icmp_socket.sendto(packet, (dest_addr, 1))
            print("packets sent to {}".format(dest_addr))

            """Receive and process ICMP ECHO REPLY packets."""
            try:
                print("in try")
                
                received_packet, addr = icmp_socket.recvfrom(1024)
                print("still in try")
                time_elapsed = time.time() - start_time
                print("still in try")
                ip_header = received_packet[:20]
                ip_version, _, _, _, _, _ = struct.unpack('!BBHHHBBH4s4s', ip_header)
                print("still..... in try")
                icmp_header = received_packet[20:28]
                icmp_type, _, _, _, _ = struct.unpack('!BBHHH', icmp_header)
                print("STILLL in try")
                if icmp_type == ICMP_ECHO_REQUEST:
                    print(f'Received packet from {addr[0]}: seq=1 time={int(time_elapsed * 1000)}ms')

                    # Update the watchdog timer
                    subprocess.call(['echo', 'reset', '|', 'nc', 'localhost', '3000'])

            except socket.timeout as e:
                print('Request timed out.')
                print(f'Exeption: {e}')
                
            time.sleep(1)

    except (socket.error, socket.gaierror, PermissionError) as e:
        print(f'Ping failed: {str(e)}')
        sys.exit(1)


def start_watchdog():
    subprocess.call(['python3', 'watchdog.py'])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python ping.py <ip>')
        sys.exit(1)

    destination = sys.argv[1]

    # Start the watchdog in a separate thread
    watchdog_thread = threading.Thread(target=start_watchdog)
    watchdog_thread.start()
    print("thread: watchdog started")

    ping(destination)

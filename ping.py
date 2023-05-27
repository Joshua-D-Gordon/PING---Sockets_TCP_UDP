import os
import sys
import socket
import struct
import select
import time
import threading
import subprocess

ICMP_ECHO_REQUEST = 8
TIME_OUT = 1
WATCHDOG_PORT = 9999
LOCAL_HOST = "localhost"

class ping:
    #constructor
    def __init__(self, id1, id2):
        self.id_1 = id1
        self.id_2 = id2
        
    #standard checksum function
    def checksum(self, source_string):
        sum = 0
        countTo = (len(source_string) // 2) * 2

        for count in range(0, countTo, 2):
            thisVal = (source_string[count + 1] << 8) + source_string[count]
            sum += thisVal & 0xffff

        if countTo < len(source_string):
            sum += source_string[len(source_string) - 1] & 0xffff

        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)

        answer = (~sum) & 0xffff
        answer = (answer >> 8) | ((answer << 8) & 0xff00)

        #converting to network byte order
        return socket.htons(answer)

    def receive_ping(self, my_socket, seq, ID, timeout):
        start_time = time.time()
        elapsed_time = time.time() - start_time
        time_left = timeout - elapsed_time
        if time_left <= 0:
            print(f"Request timed out")
            return
        try:
            ready, _, _ = select.select([my_socket], [], [], time_left)
            if ready:
                rec_packet, _ = my_socket.recvfrom(1024)
                icmp_header = rec_packet[20:28]
                type_, code_, _, packet_ID_, _ = struct.unpack("bbHHh", icmp_header)

                if packet_ID_ == ID:
                    time_sent = struct.unpack("d", rec_packet[28:36])[0]
                    ttl = struct.unpack("B", rec_packet[8:9])[0]
                    delay =  (time.time() - time_sent)*1000
                    
                    print(f"Reply from {dest_addr}: bytes=32 seq={seq} TTL={ttl} time={delay:.3f}ms")
                    
        except select.error:
            print("error in function receive ping")
            return
            



    def send_ping(self, my_socket, dest_addr, ID):
        
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, ID, 1)
        data = struct.pack("d", time.time())
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, p1.checksum(header + data), ID, 1)

        #my_socket.sendto(header+data, (dest_addr, 1))

        # Create a separate connection to the watchdog server
        
        watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            watchdog_socket.connect((LOCAL_HOST, WATCHDOG_PORT))
        except ConnectionRefusedError:
            print("Error: Connection to the watchdog server was refused.")
            # Perform necessary error handling or exit the program
            sys.exit(1)


        # Send the ping packet
        my_socket.sendto(header+data, (dest_addr, 1))
        
        # Update watchdog that ping has been sent
        watchdog_socket.sendall('sent'.encode())
        
        # Close the watchdog socket
        watchdog_socket.close()
    def ping(self,dest_addr,seq):
        #make raw socket
        try:
            icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        except:
            print("error icmp socket could not be made")
            exit(1)

        #send & recive ping
        self.send_ping(icmp_socket, dest_addr, ID=os.getpid()) # os.getpid() gets .........
        self.receive_ping(icmp_socket, seq, ID=os.getpid(), timeout=TIME_OUT) #timeout ...........
        #close socket
        icmp_socket.close()
    
    def loop_ping(self,dest_addr):
        seq = 0 #stating seqence number
        while True:
            seq += 1
            try:
                p1.ping(dest_addr,seq)#ping ip address with seqence number
                time.sleep(1)#sleep for watchdog thread
            #end pinging
            except KeyboardInterrupt:
                print("\n*********************FINISHED***************************")
                print("********************************************************")
                print("\nStudent ID's: {} & {}".format(self.id_1,self.id_2))
                exit(1)

def start_watchdog():
    subprocess.call(['python3', 'watchdog.py'])
    

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('rerun and enter a ip address to ping')
        sys.exit(1)
    
    #creats new ping object with our id's
    p1 = ping("332307073","332307074")
    #starts watchdog thread
    watchdog_thread = threading.Thread(target=start_watchdog)
    watchdog_thread.start()
    time.sleep(2)
    # recives ip address to ping
    dest_addr = sys.argv[1]
    #performs a ping loop
    p1.loop_ping(dest_addr)
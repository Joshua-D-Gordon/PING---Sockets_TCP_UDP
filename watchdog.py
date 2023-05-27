import socket
import time


WATCHDOG_PORT = 9999
WATCHDOG_TIMEOUT = 10  # Timeout in seconds
LOCAL_HOST = "localhost"

def start_watchdog():
    timer = WATCHDOG_TIMEOUT
    
    watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    watchdog_socket.bind((LOCAL_HOST, WATCHDOG_PORT))
    try:
        watchdog_socket.listen()
        connection, addr = watchdog_socket.accept()
        print('Connected by', addr)

        while True:
            data = connection.recv(1024).decode()
            if data == 'reset':
                timer = WATCHDOG_TIMEOUT
                connection.sendall('ACK'.encode())
            elif data =='sent':
                print("data sent")
            
            if timer == 0:
                break

            time.sleep(1)
            timer -= 1

        connection.sendall('END'.encode())
        print("server cannot be reached.")
        connection.close()

    except socket.error as e:
        print(f'Watchdog error: {str(e)}')


if __name__ == '__main__':
    print("STARTING WATCHDOG")
    start_watchdog()
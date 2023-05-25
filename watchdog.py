import socket
import time


WATCHDOG_PORT = 3000
WATCHDOG_TIMEOUT = 10  # Timeout in seconds


def start_watchdog():
    try:
        watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("watchdog till here 0")
        watchdog_socket.bind(('localhost', WATCHDOG_PORT))
        watchdog_socket.listen(1)
        print("watchdog till here 1")
        while True:
            connection, addr = watchdog_socket.accept()
            data = connection.recv(1024).decode()
            print("watchdog till here 2")
            if data == 'reset':
                start_time = time.time()
                connection.sendall('ACK'.encode())

                while True:
                    print("watchdog till here 3")
                    current_time = time.time()
                    elapsed_time = current_time - start_time

                    if elapsed_time >= WATCHDOG_TIMEOUT:
                        print(f'Server {addr[0]} cannot be reached.')
                        connection.close()
                        break

                    connection.sendall(str(WATCHDOG_TIMEOUT - elapsed_time).encode())
                    time.sleep(1)

            connection.close()

    except socket.error as e:
        print(f'Watchdog error: {str(e)}')


if __name__ == '__main__':
    start_watchdog()

import socket
import os
import hashlib


IP = '127.0.0.1'
PORT = 12000
BUFFER_SIZE = 1024


def get_file_info(data: bytes) -> (str, int):
    return data[8:].decode(), int.from_bytes(data[:8], byteorder='big')


def upload_file(server_socket: socket, file_name: str, file_size: int):
    sha256 = hashlib.sha256()
    with open(file_name+'.temp', 'wb') as file:
        bytes_received = 0
        while bytes_received < file_size:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            if not data:
                break

            file.write(data)

            sha256.update(data)

            server_socket.sendto(b'received', client_address)

            bytes_received += len(data)

    client_hash, client_address = server_socket.recvfrom(BUFFER_SIZE)

    with open(file_name+'.temp', 'rb') as file:
        server_hash = hashlib.sha256(file.read()).hexdigest()

    if client_hash.decode() == server_hash:
        os.rename(file_name+'.temp', file_name)
        server_socket.sendto(b'success', client_address)
    else:
        os.remove(file_name+'.temp')
        server_socket.sendto(b'failed', client_address)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f'Server ready and listening on {IP}:{PORT}')

    try:
        while True:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            file_name, file_size = get_file_info(data)
            server_socket.sendto(b'go ahead', client_address)
            upload_file(server_socket, file_name, file_size)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'An error occurred while receiving the file: {str(e)}')
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()

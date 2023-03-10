import socket
import hashlib
import sys
import os.path as path


IP = '127.0.0.1'
PORT = 12000
BUFFER_SIZE = 1024


def get_file_size(file_name: str) -> int:
    size = 0
    try:
        size = path.getsize(file_name)
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(1)
    return size


def send_file(filename: str):
    file_size = get_file_size(filename)

    size_bytes = file_size.to_bytes(8, byteorder='big')

    sha256 = hashlib.sha256()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:

        client_socket.sendto(size_bytes + filename.encode(), (IP, PORT))

        message, address = client_socket.recvfrom(BUFFER_SIZE)
        if message != b'go ahead':
            raise Exception('Bad server response - was not go ahead!')

        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(BUFFER_SIZE)
                if len(chunk) == 0:
                    break
                sha256.update(chunk)
                client_socket.sendto(chunk, (IP, PORT))
                response, address = client_socket.recvfrom(BUFFER_SIZE)
                if response != b'received':
                    raise Exception('Bad server response - was not received')


        client_socket.sendto(sha256.digest(), (IP, PORT))

        message, address = client_socket.recvfrom(BUFFER_SIZE)
        if message == b'failed':
            raise Exception('Transfer failed!')
        else:
            print('Transfer completed!')
    except Exception as e:
        print(f'An error occurred while sending the file: {e}')
    finally:
        client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'SYNOPSIS: {sys.argv[0]} <filename>')
        sys.exit(1)
    file_name = sys.argv[1]
    send_file(file_name)

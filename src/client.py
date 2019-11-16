import argparse, socket, logging, threading, concurrent.futures

# Some constants for easier testing
MAX_CLIENT_THREADS = 3

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            logging.error('Did not receive all the expected bytes from server.')
            break
        data += more
    return data

def client(host,port):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host,port))
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))

    # exchange messages
    sock.sendall(b'100 HELO')
    logging.info('Sent: 100 HELO')
    message = recvall(sock, 6).decode('utf-8') 
    logging.info('Received: ' + message)
    if message.startswith('200'):
        logging.info('This is a good thing.')
    else:
        logging.info('We sent a bad request.')

    # new code goes here


if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CLIENT_THREADS) as executor:
        for i in range(MAX_CLIENT_THREADS):
            executor.submit(client, args.host, port)

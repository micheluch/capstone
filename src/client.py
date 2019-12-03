import argparse, socket, logging, concurrent.futures, sys, time
import random

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

RED_DURATION = 10 #Variable to control the timer for red lights (in seconds)
nGreen = False
sGreen = False
eGreen = False
wGreen = False

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            logging.error('Did not receive all the expected bytes from server.')
            break
        data += more
    return data


def client(host, port, isAttacker, mode):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host ,port))
    isGreen = False
    turnRedMsg = "100"
    turnGreenMsg = "200"
    patienceValue = 1
    latency = 0
    if (isAttacker):
        if mode == 1:
            patienceValue = 0
        elif mode ==2:
            latency = 0.1
        turnRedMsg = "105"
        turnGreenMsg = "205"
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))

    # exchange messages
    sock.sendall(b'100 HELO')
    logging.info('Sent: 100 HELO')
    message = recvall(sock, 6).decode('utf-8')
    logging.info('Received: ' + message)
    if message.startswith('200'):
        logging.info('All OK')
    else:
        logging.info('We sent a bad request.')

    # REGISTRATION
    message = recvall(sock, 3).decode('utf-8')
    logging.info('Received: ' + message)
    if message.startswith('110'):
        clientRole = 'N'
        isGreen = True
        nGreen = True
        logging.info('Role is ' + clientRole)
    elif message.startswith('120'):
        clientRole = 'E'
        eGreen = False
        logging.info('Role is ' + clientRole)
    elif message.startswith('130'):
        clientRole = 'S'
        isGreen = True
        sGreen = True
        logging.info('Role is ' + clientRole)
    elif message.startswith('140'):
        clientRole = 'W'
        wGreen = False
        logging.info('Role is ' + clientRole)
    else:
        logging.info('Role is sentinel/observer: ' + message)
        clientRole = ''
        while ( (nGreen or sGreen) != (eGreen or wGreen) ):
            sendMessage = ('600').encode('utf-8')
            sock.sendall(sendMessage)
            logging.info("Sentinel: All\'s well")
        nGreen = None
        eGreen = None
        sGreen = None
        wGreen = None
        sock.sendall('700 Error Detected'.encode('utf-8'))
        logging.error('Sentinel sent: 700 Error Detected')
        sock.close()
        sys.exit()

    message = recvall(sock, 3).decode('utf-8')
    logging.info(clientRole + ' Received: ' + message)

    while True:
        if isGreen:
            message = recvall(sock, 7).decode('utf-8')
            logging.info(clientRole + ' Received: ' + message)
            if message.startswith("400"):
                isGreen = False
                if clientRole == 'N':
                    nGreen = False
                elif clientRole == 'S':
                    sGreen = False
                elif clientRole == 'E':
                    eGreen = False
                elif clientRole == 'W':
                    wGreen = False

                sendMessage = (turnRedMsg + " " + clientRole + " R").encode('utf-8')
                sock.sendall(sendMessage)
                logging.info(clientRole + ' Sent:' + sendMessage.decode('utf-8'))
            else:
                sys.exit(-1)
        else: # light is Red
            time.sleep(RED_DURATION * patienceValue)
            sendMessage = (turnGreenMsg + " " + clientRole + " G").encode('utf-8')
            sock.sendall(sendMessage)
            logging.info(clientRole + ' Sent: ' + sendMessage.decode('utf-8'))
            message = recvall(sock, 7).decode('utf-8')
            logging.info(clientRole + ' Received: ' + message)
            if message.startswith("300"):
                isGreen = True
                #if nGreen is None or sGreen is None or eGreen is None or wGren is None:
                    #sendMessage = '705 Entering Error Mode'.encode('utf-8')
                    #break
                if clientRole == 'N' and nGreen is None:
                    sock.sendall('700 a b'.encode('utf-8'))
                elif clientRole == 'N':
                    nGreen = False
                elif clientRole == 'S' and sGreen is None:
                    sock.sendall('700 a b'.encode('utf-8'))
                elif clientRole == 'S':
                    sGreen = False
                elif clientRole == 'E' and eGreen is None:
                    sock.sendall('700 a b'.encode('utf-8'))
                elif clientRole == 'E':
                    eGreen = False
                elif clientRole == 'W' and wGreen is None:
                    sock.sendall('700 a b'.encode('utf-8'))
                elif clientRole == 'W':
                    wGreen = False

            #else:
                #sys.exit(-1)
    
    while True:
        time.sleep(1)
        if clientRole == 'N':
            nGreen = False if (nGreen is None) else None
        elif clientRole == 'S':
            sGreen = False if (sGreen is None) else None
        elif clientRole == 'E':
            eGreen = False if (eGreen is None) else None
        elif clientRole == 'W':
            wGreen = False if (wGreen is None) else None

if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Basic Traffic Light Simulator')
    parser.add_argument('host', help='IP address of the server.')
    parser.add_argument('mode', type=int, help='Client attack mode. Enter 0 for normal operation.')
    args = parser.parse_args()
    attacker = 5
    if args.mode > 0:
        attacker = random.randint(0, 3)

    with concurrent.futures.ThreadPoolExecutor(4) as executor:
        for i in range(4):
            if i == attacker:
                isAttacker = True
            else:
                isAttacker = False
            executor.submit(client, args.host, port, isAttacker, args.mode)

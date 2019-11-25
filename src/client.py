import argparse, socket, logging, concurrent.futures

# Comment out the line below to not print the INFO messages
import executor as executor

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


def client(host ,port):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host ,port))
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

    # REGISTRATION
    message = recvall(sock, 3).decode('utf-8')
    logging.info('Received: ' + message)
    if message.startswith('110'):
        clientRole = 'N'
        logging.info('Role is ' + clientRole)
    elif message.startswith('120'):
        clientRole = 'E'
        logging.info('Role is ' + clientRole)
    elif message.startswith('130'):
        clientRole = 'S'
        logging.info('Role is ' + clientRole)
    elif message.startswith('140'):
        clientRole = 'W'
        logging.info('Role is ' + clientRole)
    else:
        logging.info('Received error: ' + message)
        clientRole = ''

    # GAME PLAY
    # If 300 is sent: the game starts
    message = recvall(sock, 3).decode('utf-8')
    if message.startswith('300'):
        logging.info('Recieved: 300')
        messageLength = 21
        # Get next message
        message = recvall(sock, messageLength).decode('utf-8')
        logging.info(clientRole + ' Received: ' + message)
        # Loop the current session until server has errors or game ends normally
        while clientRole != '' and not (message.startswith('600')) and not (message.startswith('611')) and not (message.startswith('621')):
            # Case for accepted moves
            if message.startswith('320') or message.startswith('340'):
                messageLength = 21
                logging.info('Player ' + clientRole + " has moved, rejoice")
            # Case for specific player to move (X or O)
            elif (message.startswith('310') and clientRole is 'X') or (message.startswith('330') and clientRole is 'O'):
                messageLength = 5
                boardState = (message.split()[1]).split(',')
                attemptedMove = makeMove(boardState)
                send_msg = ('100 ' + str(attemptedMove)).encode('utf-8')
                sock.sendall(send_msg)
                logging.info('Sent: 100 ' + str(attemptedMove))
            # Case for player not making a valid move on their turn
            elif (message.startswith('312') and clientRole is 'X') or (message.startswith('332') and clientRole is 'O'):
                messageLength = 5
                boardState = (message.split()[1]).split(',')
                attemptedMove = makeMove(boardState)
                send_msg = ('100 ' + str(attemptedMove)).encode('utf-8')
                sock.sendall(send_msg)
                logging.info('Sent: 100 ' + str(attemptedMove))
            # Case for any invalid move a player did
            elif message.startswith('311') or message.startswith('312') or message.startswith('313'):
                logging.error(clientRole + " made an invalid move")
                attemptedMove = makeMove(boardState)
                send_msg = ('100 ' + str(attemptedMove)).encode('utf-8')
                sock.sendall(send_msg)
                logging.info('Sent: 100 ' + str(attemptedMove))
            # Case for a player moving out of turn
            elif message.startswith('314'):
                logging.info('Not ' + clientRole + "'s turn")
                messageLength = 21
            else:
                pass
            # Receive the response message
            message = recvall(sock, messageLength).decode('utf-8')
            logging.info(clientRole + ' Received: ' + message)


    # END OF GAME
    # If 600, game ended well
    if message.startswith('600'):
        message = recvall(sock, 3).decode('utf-8')
        if message.startswith('610'):
            logging.info('X won the game!')
        if message.startswith('620'):
            logging.info('O won the game!')
        if message.startswith('630'):
            logging.info('There was a tie!')

    # Quit
    sock.close()

# Function to let a player make the move
def makeMove(boardState):
    return input("Enter your move (0-8): ")

if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        for i in range(4):
            executor.submit(client, args.host, port)
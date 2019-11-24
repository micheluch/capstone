import argparse, socket, logging, threading
from engine import TicTacToeEngine

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):
    assignedX = False
    assignedO = False
    game = TicTacToeEngine()
    eventX = threading.Event()
    eventO = threading.Event()
    roleLock = threading.Lock()
    engineLock = threading.Lock()


    def __init__(self, address, socket):
        threading.Thread.__init__(self)
        self.csock = socket
        logging.info('New connection added.')

    def run(self):
        # exchange messages
        message = self.recvall(8)
        msg = message.decode('utf-8')
        logging.info('Recieved a message from client: ' + msg)

        if msg.startswith('100'):
            self.csock.sendall(b'200 OK')
            logging.info('Recieved HELO ok from client.')
        else:
            self.csock.sendall(b'500 BAD REQUEST')
            logging.warning('Bad request from client.')

        # Pre-game
        # Assign roles to players
        global XisTaken, OisTaken
        with ClientThread.roleLock:
            if XisTaken:
                self.role = 'O'
                OisTaken = True
                ClientThread.eventO.clear()
                self.csock.sendall(b'130')
            elif not OisTaken:
                self.role = 'X'
                XisTaken = True
                ClientThread.eventX.clear()
                self.csock.sendall(b'120')
            else: #In case there is a third player trying to connect
                self.csock.sendall(b'113')

        # Game on
        # Send 300: game start trigger
        message = '300'.encode('utf-8')
        self.csock.sendall(message)
        logging.info('Sent: 300')
        ClientThread.game.display_board()
        # Main loop of the game
        while self.role != '' and ClientThread.game.is_game_over() == '-':
            # XOR for X and O clients, so the game doesn't deadlock
            if (self.role is 'X' and ClientThread.game.x_turn is True) or not (
                        self.role is 'X' or ClientThread.game.x_turn is True):
                if ClientThread.game.x_turn is True:
                    ID = '310 ' # for X
                else:
                    ID = '330 ' # for O
                # Send current board to players and receive their responses
                currentBoard = ','.join(ClientThread.game.board)
                outgoingMessage = (ID + currentBoard).encode('utf-8')
                self.csock.sendall(outgoingMessage)
                logging.info('Sent: ' + ID + currentBoard)
                message = self.recvall(5)
                msg = message.decode('utf-8')
                logging.info('Received message: ' + msg)
                attemptedMove = int(msg.split()[1])
                # Check if player made an illegal move
                while not ClientThread.game.is_move_valid(attemptedMove):
                    if ClientThread.game.x_turn is True:
                        ID = '312 ' # for X
                    else:
                        ID = '332 ' # for O
                    currentBoard = ','.join(ClientThread.game.board)
                    outgoingMessage = (ID + str(attemptedMove)).encode('utf-8')
                    self.csock.sendall(outgoingMessage)
                    logging.info('Sent: ' + ID + currentBoard)
                    message = self.recvall(5)
                    msg = message.decode('utf-8')
                    logging.info('Received message: ' + msg)
                    attemptedMove = int(msg.split()[1])
                # Once the move is made, send confirmation that it was registered
                if ClientThread.game.x_turn is True:
                    ID = '320  '
                else:
                    ID = '340  '
                # Actually register the move
                with ClientThread.engineLock:
                    ClientThread.game.make_move(attemptedMove)
                outgoingMessage = ID.encode('utf-8')
                self.csock.sendall(outgoingMessage)
                logging.info('Sent: ' + ID)

        # END OF GAME
        # Send the endgame message to clients (600)
        currentBoard = ','.join(ClientThread.game.board)
        outgoingMessage = ('600 ' + currentBoard).encode('utf-8')
        self.csock.sendall(outgoingMessage)
        logging.info('Sent: 600: Game concluded')
        # Send a personalized message to clients about who won
        if ClientThread.game.is_game_over() is 'X':
            outgoingMessage = '610'.encode('utf-8')
            self.csock.sendall(outgoingMessage)
            logging.info('Sent: 610 X won!')
        elif ClientThread.game.is_game_over() is 'O':
            outgoingMessage = '620'.encode('utf-8')
            self.csock.sendall(outgoingMessage)
            logging.info('Sent: 620 O won!')
        else:
            outgoingMessage = '630'.encode('utf-8')
            self.csock.sendall(outgoingMessage)
            logging.info('Sent: 630 T-1000 won! (I\'ll be back)')

        # Kick everybody out and clean the place up for the next players
        if self.role == 'X':
            XisTaken = False
        else:
            OisTaken = False
        if self.role == 'X':
            ClientThread.eventX.set()
            ClientThread.eventO.wait()
        elif self.role == 'O':
            ClientThread.eventO.set()
            ClientThread.eventX.wait()
        ClientThread.game.restart()
        self.csock.close()
        logging.info('Disconnected client: ' + self.role)


    def recvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data))
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
        return data


def server():
    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost' ,port))

    while True:
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))

        # client has connected
        sc ,sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc)
        t.start()

# Initiate the server
XisTaken = False
OisTaken = False
server()
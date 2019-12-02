import argparse, socket, logging, threading
import time

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):

    lightToChange = threading.Lock()
    changeMutex = threading.Lock()
    roleLock = threading.Lock()

    changeLight = False

    NChangeEvent = threading.Event()
    SChangeEvent = threading.Event()
    EChangeEvent = threading.Event()
    WChangeEvent = threading.Event()

    NisTaken = False
    EisTaken = False
    SisTaken = False
    WisTaken = False
        
    def __init__(self, address, socket):
        threading.Thread.__init__(self)
        self.addr = address
        self.csock = socket
        self.isGreen = False
        logging.info('New connection added.')

    def run(self):
        # exchange messages
        message = self.recvall(8)
        msg = message.decode('utf-8')
        logging.info('Received a message from client: ' + msg)

        if msg.startswith('100'):
            self.csock.sendall(b'200 OK')
            logging.info('Received HELO ok from client.')
        else:
            self.csock.sendall(b'500 BAD REQUEST')
            logging.warning('Bad request from client.')

        # Pre-connection
        # Assign traffic light
        with ClientThread.roleLock:
            if not ClientThread.NisTaken:
                self.role = 'N'
                ClientThread.NisTaken = True
                self.isGreen = True
                self.csock.sendall(b'110')
            elif not ClientThread.EisTaken:
                self.role = 'E'
                ClientThread.EisTaken = True
                self.csock.sendall(b'120')
            elif not ClientThread.SisTaken:
                self.role = 'S'
                ClientThread.SisTaken = True
                self.isGreen = True
                self.csock.sendall(b'130')
            elif not ClientThread.WisTaken:
                self.role = 'W'
                ClientThread.WisTaken = True
                self.csock.sendall(b'140')
            else:
                # Client is now a sentinel/observer
                self.csock.sendall(b'105')
                self.role = ''
#                working = True
#                while working:
#                    message = self.recvall(3).decode('utf-8')
#                    if message.startswith("700"):
#                        message = self.recvall(15).decode('utf-8')
#                        NChangeEvent.set()
#                        SChangeEvent.set()
#                        EChangeEvent.set()
#                        WChangeEvent.set()
#                        working = False
#                    else:
#                        message = self.recvall(9).decode('utf-8')
#                    logging.info("Sentinel sent " + message)
#                sock.close()
#                sys.exit()

        if self.role == '':
            working = True
            while working:
                message = self.recvall(3).decode('utf-8')
                if message.startswith("700"):
                    message = self.recvall(15).decode('utf-8')
                    NChangeEvent.set()
                    SChangeEvent.set()
                    EChangeEvent.set()
                    WChangeEvent.set()
                    working = False
                else:
                    message = self.recvall(9).decode('utf-8')
                logging.info("Sentinel sent " + message)
            sock.close()
            sys.exit()



        # Game on
        # Send 300: game start trigger
        message = '900'.encode('utf-8')
        self.csock.sendall(message)
        logging.info('Sent: 900')

        # Main loop of the Traffic Light simulation
        while True:
            if self.isGreen:
                if (self.role is 'N') or (self.role is 'S'):
                    ClientThread.EChangeEvent.wait()
                    ClientThread.WChangeEvent.wait()
                elif (self.role is 'E') or (self.role is 'W'):
                    ClientThread.NChangeEvent.wait()
                    ClientThread.SChangeEvent.wait()
                message = ("400 " + self.role + " R").encode('utf-8')
                self.csock.sendall(message)
                logging.info('Sent to ' + self.role + ': 400 ' + self.role + ' R')
                message = self.recvall(7).decode('utf-8')
                if message.startswith('700'):
                    #message += self.recvall(15).decode('utf-8')
                    logging.error('Received fatal error from ' + self.role + ': ' + message)
                    break
                #else:
                #    message += self.recvall(4).decode('utf-8')
                logging.info('Received from ' + self.role + ': ' + message)
                self.isGreen = False
                
                if self.role is 'N':
                    #set NChangeEvent
                    ClientThread.NChangeEvent.set()
                if self.role is 'S':
                    #set SChangeEvent
                    ClientThread.SChangeEvent.set()
                if self.role is 'E':
                    #set EChangeEvent
                    ClientThread.EChangeEvent.set()
                if self.role is 'W':
                    #set WChangeEvent
                    ClientThread.WChangeEvent.set()
 
            else:
                message = self.recvall(7).decode('utf-8')
                if message.startswith('700'):
                    #message += self.recvall(15).decode('utf-8')
                    logging.error('Received fatal error from ' + self.role + ': ' + message)
                #else:
                #    message += self.recvall(4).decode('utf-8')
                logging.info('Received from ' + self.role + ': ' + message)
                if self.role is 'N':
                    #set NChangeEvent
                    ClientThread.NChangeEvent.set()
                if self.role is 'S':
                    #set SChangeEvent
                    ClientThread.SChangeEvent.set()
                if self.role is 'E':
                    #set EChangeEvent
                    ClientThread.EChangeEvent.set()
                if self.role is 'W':
                    #set WChangeEvent
                    ClientThread.WChangeEvent.set()
                #wait on NChangeEvent
                ClientThread.NChangeEvent.wait()
                #wait on SChangeEvent
                ClientThread.SChangeEvent.wait()
                #wait on EChangeEvent
                ClientThread.EChangeEvent.wait()
                #wait on WChangeEvent
                ClientThread.WChangeEvent.wait()
                #clear all events

                time.sleep(1) #Removing the sleep desynchronizes the system. Potential break for machine learning alrgorithm to catch

                ClientThread.NChangeEvent.clear()
                ClientThread.SChangeEvent.clear()
                ClientThread.EChangeEvent.clear()
                ClientThread.WChangeEvent.clear()

                message = ("300 " + self.role + " G").encode('utf-8')
                self.csock.sendall(message)
                logging.info('Sent to ' + self.role + ': 300 ' + self.role + ' G')
                self.isGreen = True


    def recvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data))
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
        return data

    def qrecvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data), socket.MSG_DONTWAIT)
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
server()

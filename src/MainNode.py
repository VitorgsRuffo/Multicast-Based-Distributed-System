import sys
import socket
import threading
import pickle

class MainNode:
    # 2. instantiate socket and nodes list...
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen()
        self.socket.settimeout(2)
        self.nodes_list = []
        self.lock = threading.Lock()

    #3.1. open new thread for processing request...
    def __node_thread(self, conn, addr):
        
        #3.1.1 return nodes list...
        # Sending list as a string
        data = str(self.nodes_list)
        data = data.encode()
        conn.send(data)


        #3.1.2. wait for confirmation of connection...
        try:
            # True: add new node to nodes list using a Lock...
            conn.recv(2048)
            self.lock.acquire()
            self.nodes_list.append(addr)
            self.lock.release()

        except:
            print("Node " + addr + " failed to connect to the system.")


        # close connection...
        conn.close()


    #3. wait for new node...
    def execute(self):
        while True:
            conn, addr = self.socket.accept()
            new_thread = threading.Thread(self.__node_thread,(conn, addr))
            new_thread.start()

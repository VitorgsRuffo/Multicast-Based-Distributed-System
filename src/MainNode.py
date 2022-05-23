import sys
import socket
from _thread import *
import threading

class MainNode:
    # 2. instantiate socket and nodes list...
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen()
        self.nodes_list = []
        self.lock = threading.Lock()

    #3.1. open new thread for processing request...
    def __node_thread(self, conn, addr):
        
        #3.1.1 return nodes list...
        # Sending list as a string
        data = str(self.nodes_list)
        data = data.encode('utf-8')
        conn.send(data)


        #3.1.2. wait for confirmation of connection...
        
        # True: add new node to nodes list using a Lock...
        original_port = conn.recv(2048)
        original_port = int(original_port.decode())

        if(original_port < 0):    
            print("Node " + addr + " failed to connect to the system.")
        else:
            self.lock.acquire()
            self.nodes_list.append(addr)
            self.lock.release()

        # close connection...
        conn.close()


    #3. wait for new node...
    def execute(self):
        while True:
            conn, addr = self.socket.accept()
            start_new_thread(self.__node_thread,(conn, addr))

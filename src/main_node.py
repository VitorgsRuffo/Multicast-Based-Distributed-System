#1. process execution parameters...
#2. instantiate socket and nodes list...
#3. wait for new node...
    #3.1. open new thread for processing request...
        #3.1.1 return nodes list...
        #3.1.2. wait for confirmation of connection...
            # True: add new node to nodes list using a Lock...
        #3.1.3. close connection...


import sys
import socket
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
        self.lock.acquire()
        
        #3.1.2. wait for confirmation of connection...
        try:
            # True: add new node to nodes list using a Lock...
            conn.recv(2048)
            self.nodes_list.append(addr)

        except:
            print("Failed to connect node " + addr)

        self.lock.release()

        

    #3. wait for new node...
    def execute(self):
        
        while True:
            self.socket.settimeout(5)
            conn, addr = self.socket.accept()

            new_thread = threading.Thread(self.__node_thread,(conn, addr))
            new_thread.start()

            #3.1.3. close connection...
            conn.close()



# 1. process execution parameters...
ip_address = str(sys.argv[1])
port = int(sys.argv[2])

main_node = MainNode(ip_address, port)
main_node.execute()

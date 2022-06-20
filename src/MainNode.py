import sys
import socket
from _thread import *
import threading
import json
import time
from GraphVisualization import GraphVisualization

class MainNode:
    # 2. instantiate socket and nodes list...
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen()
        self.nodes_list = []
        self.lock = threading.Lock()
        self.self_address = (ip, port)
        #this is the global distribuited system abstract representation for future failure handling...
        self.distributed_system = {}
        self.buffer = []
    
    def __send_nodes_list(self, conn):
        # Sending nodes list as a string
        data = str(self.nodes_list)
        data = data.encode('utf-8')
        conn.send(data)

    # function for processing new node request...
    def __node_connection(self, conn, addr):
        
        # sending nodes_list to new node connection
        self.__send_nodes_list(conn)

        # wait for confirmation of connection (i.e., the two control messages below: msg1 and msg2)...
        # msg1: original port.
        # adding new node to 
        original_port = conn.recv(1024)
        original_port = original_port.decode()        
        original_port = int(original_port)

        new_node_original_addr = (addr[0], original_port)
        if original_port < 0 :  
            print("Node " + str(new_node_original_addr) + " failed to connect to the system.")
        else:
            self.lock.acquire()
            self.nodes_list.append(new_node_original_addr)
            self.lock.release()
        
        
        # msg2: the other node this node has connected with.
        # maintaining the distributed system topology in main node for future failure handling...
        new_node_connection = conn.recv(1024)
        new_node_connection = new_node_connection.decode()
        new_node_original_addr_string = f"{new_node_original_addr[0]}:{new_node_original_addr[1]}"
        print(new_node_connection)
        if new_node_connection == "0:0":
            self.distributed_system[new_node_original_addr_string] = []
            #start_new_thread(self.__checkConnections, ())
        else:
            self.distributed_system[new_node_connection].append(new_node_original_addr_string)
            self.distributed_system[new_node_original_addr_string] = []
            self.distributed_system[new_node_original_addr_string].append(new_node_connection)
            start_new_thread(self.__distributed_system_visualization, (self.distributed_system,))
        
        # Waiting for request from other nodes to access shared buffer (To produce or consume)
        while True:
            try:
                request = conn.recv(1024).decode()
                request = json.loads(request)
            except: 
                request = ''

            if request['type'] == 'consume':
                print(f'\nbuffer: {self.buffer}')
                print('***Consuming content on buffer...***')
                try:
                    data = self.buffer.pop(0)
                    conn.send(data.encode())
                except:
                    conn.send('Buffer está vazio'.encode())
                print(f'buffer: {self.buffer}')

            elif request['type'] == 'produce':
                print(f'\nbuffer: {self.buffer}')
                print('***Producing content to buffer...***')
                data_produced = request['data']
                self.buffer.append(data_produced)
                print(f'buffer: {self.buffer}')
                conn.send('OK'.encode())

            elif request['type'] == 'get_list':
                self.__send_nodes_list(conn)
                

        # close connection...
        #conn.close()

    def __distributed_system_visualization(self, distributed_system):
        G = GraphVisualization(distributed_system)
        G.visualize()

    def __checkConnections(self):
        new_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_connection.bind((self.self_address[0], 21001))
        #socket.setdefaulttimeout(5)

        request_data = {'type_connection':'check_connection'}
        request = json.dumps(request_data).encode()
        time.sleep(5)

        while True:
            if(len(self.nodes_list) > 0):
                for node_address in self.nodes_list:
                    new_connection
                    
            time.sleep(5)


    #3. wait for new node...
    def execute(self):
        print("Main node running...")
        
        while True:
            conn, addr = self.socket.accept()
            start_new_thread(self.__node_connection, (conn, addr))

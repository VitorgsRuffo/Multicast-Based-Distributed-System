from copyreg import pickle
import socket
import select
import sys
from _thread import *
import threading 
import os
import re
import subprocess

class Node:
    def __init__(self, main_node_address, self_address):
        #. instantiate two sockets and connections list...
        self.self_address = self_address
        self.lock = threading.Lock()
        self.first_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection_socket.bind(self_address)
        self.connection_socket.listen(100) 
        self.connections = []
        
        #. nodes_list = connect to the DS (main_node)...
        main_node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_node_socket.connect(main_node_address)
        main_node_socket.send("c".encode())

        # receiving list from a main_node as string and converting to list
        data = main_node_socket.recv(4096)
        data = data.decode('utf-8')
        main_nodes_list = eval(data)

        connection_addr = "0:0"

        #if nodes_list not empty:
        if len(main_nodes_list) > 0:
            
            #. best_connection = get_node_with_minimum_ping(nodes_list)...
            best_connection = self.get_node_with_minimum_ping(main_nodes_list)
            
            #. if best_connection == None: exit(1)
            if best_connection == None:
                main_node_socket.send('-1'.encode())
                exit(1)

            #. try{ self.first_connection_sockets.connect(best_connection)} except{exit(1)}
            try:
                self.first_connection_socket.connect(best_connection)
                #. connections_list.add(first_connection_socket)...
                self.connections.append(self.first_connection_socket)
                connection_addr = f"{best_connection[0]}:{best_connection[1]}"
            except:
                main_node_socket.send('-1'.encode())
                print("Failed to connect.")
                exit(1)
        
        #. send connection confirmation to main_node...
        main_node_socket.send(f'{self_address[1]}'.encode())
        main_node_socket.send(connection_addr.encode())
        main_node_socket.close()
        

    def get_node_with_minimum_ping(self, main_nodes_list):
        addr_with_lowest_latency = None
        lowest_latency = None
        
        for addr_node in main_nodes_list:
            # getting ping latency
            response = str(subprocess.check_output(['ping', '-c', '1', addr_node[0]]))

            latency = re.search(r'(\d+\.\d+/){3}\d+\.\d+', response).group(0)
            latency = float(latency.split('/')[0])

            if lowest_latency == None:
                lowest_latency = latency
                addr_with_lowest_latency = addr_node
            else:
                if latency < lowest_latency:
                    lowest_latency = latency
                    addr_with_lowest_latency = addr_node

        return addr_with_lowest_latency

    # (main thread): sending message to connections...
    def start(self):
        # starting thread 2...
        start_new_thread(self.__wait_for_incoming_connections, ())

        # starting thread 3...
        start_new_thread(self.__wait_for_incoming_messages, ())

        while True:
            _, _, _ = select.select([sys.stdin],[],[])
            message = sys.stdin.readline()
            message = f"<{self.self_address[0]}:{self.self_address[1]}> {message}"
            self.__multicast(message.encode(), None)
            sys.stdout.write("<This node>")
            sys.stdout.write(message)
            sys.stdout.flush()


    def __multicast(self, message, sending_connection):
        self.lock.acquire()
        connections = self.connections #*****shared variable*******
        self.lock.release()
        for connection in connections:
            if connection != sending_connection:
                connection.send(message)
    

     # (thread 2): waiting for incoming connections...
    def __wait_for_incoming_connections(self): 
        while True:
            conn, addr = self.connection_socket.accept()
            self.lock.acquire()
            self.connections.append(conn)  #*****shared variable*******
            self.lock.release()


    # (thread 3): wait for incoming messages and cast to connections...
    def __wait_for_incoming_messages(self):
        while True:
            self.lock.acquire()
            connections = self.connections #*****shared variable*******
            self.lock.release()
            incoming_message_connections, _, _= select.select(connections, [], [], 0.5) 
            for incoming_message_connection in incoming_message_connections:
                message = incoming_message_connection.recv(1024)
                sys.stdout.write(message.decode())
                sys.stdout.flush()
                self.__multicast(message, incoming_message_connection)

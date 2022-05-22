import socket
import select
import sys
from _thread import *
import threading 

class Node:

    def __init__(self, main_node_address, self_address):
        #. instantiate two sockets and connections list...
        self.self_address = self_address
        self.lock = threading.Lock()
        self.first_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection_socket.bind(self_address)
        self.connection_socket.listen(100) 
        self.connections = []
        
        #. nodes_list = connect to the DS (main_node)...
        #if nodes_list not empty:
            #. best_connection = get_node_with_minimum_ping(nodes_list)...
            #. if best_connection == null: exit(1)
            #. try{ self.first_connection_sockets.connect(best_connection)} except{exit(1)}
            #. connections_list.add(first_connection_socket)...
        #. send connection confirmation to main_node...


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
            self.__multicast(message, None)
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
                sys.stdout.write(message)
                sys.stdout.flush()
                self.__multicast(message, incoming_message_connection)


#1. process execution parameters...

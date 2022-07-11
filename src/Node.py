import socket
import select
import sys
from _thread import *
import threading 
import json
import time
import re
import subprocess
from time import sleep

class Node:
    def __init__(self, main_node_address, self_address):
        # instantiate two sockets and connections list...
        self.self_address = self_address
        self.lock = threading.Lock()
        self.first_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection_socket.bind(self_address)
        self.connection_socket.listen(100) 
        self.connections = []
        self.main_node_connection = ''
        self.node_type = ''
        self.node_type_act = ''
        self.is_using_shared_memory = 0

        # Definig if node is producer or consumer
        while True:
            print("Producer or Consumer? [p|c]")
            self.node_type = input()

            if(self.node_type == 'p' or self.node_type == 'P'):
                self.node_type_act = self.__produce
                break
            elif(self.node_type == 'c' or self.node_type == 'C'):
                self.node_type_act = self.__consume
                break
            print("Invalid Option... Try again")

        
        # nodes_list = connect to the DS (main_node)...
        main_node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_node_socket.connect(main_node_address)

        # receiving list from a main_node as string and converting to list
        data = main_node_socket.recv(4096)
        data = data.decode('utf-8')
        main_nodes_list = eval(data)

        connection_addr = "0:0"

        if len(main_nodes_list) > 0:
            best_connection = self.get_node_with_minimum_ping(main_nodes_list)
            
            if best_connection == None:
                main_node_socket.send('-1'.encode())
                exit(1)

            try:
                self.first_connection_socket.connect(best_connection)
                request_data = {'type_connection':'connect'}
                request = json.dumps(request_data).encode()
                self.first_connection_socket.send(request)
                self.connections.append(self.first_connection_socket)
                connection_addr = f"{best_connection[0]}:{best_connection[1]}"
            except:
                main_node_socket.send('-1'.encode())
                print("Failed to connect.")
                exit(1)
        
        # send connection confirmation to main_node...
        main_node_socket.send(f'{self_address[1]}'.encode())
        sleep(1)
        main_node_socket.send(connection_addr.encode())
        self.main_node_connection = main_node_socket

    def __produce(self):
        print("Producing...")
        self.is_using_shared_memory = 1

        # check if somebody is using shared memory
        status = self.check_shared_memory_use(self.main_node_connection)

        if status is True:
            # send operation type and data to main node and wait reponse
            data = f'content from {self.self_address}'
            request_data = {"type":"produce", "data":data}
            request = json.dumps(request_data).encode()
            self.main_node_connection.send(request)

            # when coming response, change 'is using' to 0
            response = self.main_node_connection.recv(1024)
            if(response.decode() == 'OK'):
                self.is_using_shared_memory = 0
                print("Success!")
                return True
            else:
                return False

    def __consume(self):
        print("Consuming...")
        self.is_using_shared_memory = 1

        # check if somebody is using shared memory
        status = self.check_shared_memory_use(self.main_node_connection)

        if status is True:
            # send operation type to main node e wait response
            request_data = {"type":"consume"}
            request = json.dumps(request_data).encode()
            self.main_node_connection.send(request)
            reponse = self.main_node_connection.recv(4096)
            
            # print response and change 'is using' to 0
            print('Consumed message: '+reponse.decode())
            self.is_using_shared_memory = 0
        

    def get_node_with_minimum_ping(self, main_nodes_list):
        addr_with_lowest_latency = None
        lowest_latency = None
        
        for addr_node in main_nodes_list:
            if addr_node != self.self_address:
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
        
        if addr_with_lowest_latency is not None:
            print("Best Connection: "+ str(addr_with_lowest_latency))
        
        return addr_with_lowest_latency


    # (main thread): sending message to connections...
    def start(self):
        print("Node running...")
        # starting thread 2...
        start_new_thread(self.__wait_for_incoming_connections, ())

        # starting thread 3...
        start_new_thread(self.__wait_for_incoming_messages, ())

        while True:
            _, _, _ = select.select([sys.stdin],[],[])
            message = sys.stdin.readline()

            if (message == 'consume\n') or (message == 'produce\n'):
                start_new_thread(self.node_type_act, ())

            else:
                message = f"<{self.self_address[0]}:{self.self_address[1]}> {message}"
                self.__multicast(message.encode(), None)
                sys.stdout.write("<This node>")
                sys.stdout.write(message)
                sys.stdout.flush()


    def __multicast(self, message, sending_connection):
        self.lock.acquire()
        connections = self.connections # *****shared variable*******
        self.lock.release()
        for connection in connections:
            if connection != sending_connection:
                connection.send(message)
    

    def check_shared_memory_use(self, main_node_connection):
        # send message to main node requesting nodes_list and receive response
        request_data = {'type':'get_list'}
        request = json.dumps(request_data).encode()
        main_node_connection.send(request)
        nodes_list = main_node_connection.recv(4096)
        nodes_list = nodes_list.decode('utf-8')
        nodes_list = eval(nodes_list)
        
        for node in nodes_list:
            if node != self.self_address:
                print(f'Connecting to {node}')
                # loop in nodes_list asking if its using or want to use shared memory
                socket_to_check_sm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_to_check_sm.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                socket_to_check_sm.bind((self.self_address[0], int(50000)))
                # set timeout to receive response, if no receive a response so it lost connection
                socket_to_check_sm.settimeout(2)

                # Handling with connection concorrency
                while True:
                    try:
                        socket_to_check_sm.connect(node)
                        break
                    except:
                        print(f'Outro cliente está acessando {node}, aguarde um momento...')
                        time.sleep(0.5)
                    
                data = {"type_connection":"sm"}
                data = json.dumps(data).encode()
                socket_to_check_sm.send(data)
                
                while True:
                    print(f'Checking if {node} is using shared memory...')
                    try:
                        time.sleep(0.5) # synchronizing
                        socket_to_check_sm.send(f'using?'.encode())
                        # Wait a reponse
                        response = socket_to_check_sm.recv(1024).decode()
                        if response == 'yes':
                            self.is_using_shared_memory = 0
                            time.sleep(1)
                        else:
                            self.is_using_shared_memory = 1
                            socket_to_check_sm.close()
                            break
                    
                    except:
                        print(f'Connection with {node[0]}:{node[1]} lost...')
                        return False

        # when to release acess, return true
        return True


     # (thread 2): waiting for incoming connections...
    def __wait_for_incoming_connections(self): 
        while True:
            conn, addr = self.connection_socket.accept()
            new_connection_request = conn.recv(1024).decode()
            new_connection_request = json.loads(new_connection_request)

            # Check if acess want to check shared memory use ('sm' = shared memory)
            if new_connection_request['type_connection'] == 'sm':
                # starting thread 4...
                start_new_thread(self.__wait_for_shared_memory_use, (conn, addr))
            
            elif new_connection_request['type_connection'] == 'check_connection':
                time.sleep(0.2)
                conn.send('ok'.encode())
                conn.close()

            # Just establish connection to send chat messages
            else:
                self.lock.acquire()
                self.connections.append(conn)  #*****shared variable*******
                self.lock.release()


    # (thread 3): wait for incoming messages and cast to connections...
    def __wait_for_incoming_messages(self):
        while True:
            self.lock.acquire()
            connections = self.connections # *****shared variable*******
            self.lock.release()
            incoming_message_connections, _, _= select.select(connections, [], [], 0.5) 
            for incoming_message_connection in incoming_message_connections:
                message = incoming_message_connection.recv(1024)
                sys.stdout.write(message.decode())
                sys.stdout.flush()
                self.__multicast(message, incoming_message_connection)

    # (thread 4): waiting for incoming messages to check if shared memory is using...
    def __wait_for_shared_memory_use(self, conn, addr):
        while True:
            # receive message requesting status
            conn.recv(1024)

            # if status of 'wait' or 'using' variables is 1, send 'yes'
            if self.is_using_shared_memory == 1:
                conn.send('yes'.encode())

            # else send 'no' and close connection
            else:
                conn.send('no'.encode())
                conn.close()
                break

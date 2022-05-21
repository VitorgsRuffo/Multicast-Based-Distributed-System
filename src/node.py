
#obs: whenever acessing connections list a thread must use a lock.

#1. process execution parameters...
#2. init():
    #. instantiate two sockets and connections list...
    #. nodes_list = connect to the DS (main node request)...
    #if nodes_list not empty:
        #. best_connection = get_node_with_minimum_ping(nodes_list)...
        #. if best_connection == null: exit(1)
        #. try{ connect to best_connection...} except{exit(1)}
        #. connections_list.add(best_connection)...
    #. send connection confirmation to main_node...

#3. start():
    
    #1.(sec thread) wait for incoming messages and cast to connections...
        #while True:
            # incoming_message_connections, _, _= select.select(connections_list, [], [], 2.0) 
            # for incoming_message_connection in incoming_message_connections:
                #msg = incoming_message_connection.recv()
                #print(msg)
                #for connection in connections_list:
                    #if connection != incoming_message_connection
                        #connection.send(msg)

    #2. (sec thread) wait for incoming connections...
        #  while True:
        #    conn, addr = socket.accept()
        #    connections_list.append(conn)

    #3. (main thread) send message to connections...
        #while True:
            #stdinput, _, _ = select.select(sys.stdin,[],[])
            #msg = sys.stdin.readline()
            #msg = msg.format()
            #for connection in connections_list:
                #connection.send(msg)

            #sys.stdout.write("<This node>")
            #sys.stdout.write(msg)
            #sys.stdout.flush()

#4. treatment_lost_connection():
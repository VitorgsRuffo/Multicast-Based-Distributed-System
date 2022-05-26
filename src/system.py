#Main node doesn't not take part in the distributed system message forwarding system. 
# It is used as a control node for performing tasks like adding a new node the the system and
# handling node failure.

# Nodes compose the distributed system message forwarding system. 

import sys
from MainNode import MainNode
from Node import Node

# checking execution arguments...
argvlen = len(sys.argv)
if (argvlen < 4) or (argvlen < 6 and sys.argv[1] == "normal"):
    print(f"Invalid execution format.\nUsage: python3 {sys.argv[0]}.py -mode=(main|normal) main_ip main_port [this_ip this_port]\n\tps: when mode=main this ip and port shouldn't be entered. On the other hand, when mode=normal they must be passed.\n")
    quit(1)

# getting execution arguments...
mode = sys.argv[1]
main_ip = sys.argv[2]
main_port = sys.argv[3] 
this_ip = None
this_port = None
if argvlen > 5:
    this_ip = sys.argv[4]
    this_port = sys.argv[5] 

#executing the system...
if mode == "-mode=main":
    main_node = MainNode(main_ip, int(main_port))
    main_node.execute()
elif mode == "-mode=normal":
    node = Node((main_ip, int(main_port)), (this_ip, int(this_port)))
    node.start()
else:
    print("Invalid mode.")
    quit(1)

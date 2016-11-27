import argparse
import socket
import select
import time
import sys
import random

#global constants
UPDATE_INTERVAL = 1 #set at 1 second
ROUTE_UPDATE_INTERVAL = 30* UPDATE_INTERVAL


class dataSeg:

    def __init__(self,first, recent, num, data):
        self.first = first
        self.recent = recent
        self.num = num
        self.data = data
        self.timeSent = time.time()

#Takes in the 3 flags SYN,ACK,FIN and also takes in the Segment and Ack numbers. Outputs a 5 byte header to be attached to the appropriate packet

def main():
    #doing parsing of args
    parser = argparse.ArgumentParser()
    parser.add_argument("nodeName", help= "the name of this node")
    parser.add_argument("port", help=" the port number for this node")
    parser.add_argument("configName", help="the name of the text file that has the configuration for this node")
  
    args = parser.parse_args()
    myName = args.nodeName
    PORT = int(args.port)
    socket.setdefaulttimeout(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,0)#make udp socket and use it to connect
    s.bind(("",PORT))
    s.setblocking(False)
            
    #dealing with file formatting and splitting for initial graph generation
    f = open( args.configName,'rb')
    fileTxt = f.read().split('\n')
    f.close()
    dictMap = {}
    graph = { myName: {} }
    temp = []
    for line in fileTxt:
        temp = line.split(' ')
        if len(temp) != 1:
            graph[temp[0]] = {myName : temp[1]}
            dictMap[temp[0]] = temp[2]
            graph[myName][temp[0]] = temp[1]
    print graph
    print dictMap
    sendingDistances = graph[myName]
    # print str(sendingDistances)
    # test = str(sendingDistances)
    # test2 = eval(test)
    # print test2
    # print test == sendingDistances

#timing considerations
    STARTTIME = time.time()
    prevsent = STARTTIME
        #Main loop where data is sent
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
    #setting variables we'll need before the loop starts
   
    print "Node started..."
    while True:

        readable, writable, err = select.select([s],[s],[s]) #using select to poll our socket to see if it is readable

        for sock in writable:#if s is writable (it should be), there are packets in the send queue AND one of the next two conditions is met:
            if time.time() - UPDATE_INTERVAL > prevsent:
                for key,value in dictMap.iteritems():
                    idRand = random.randint(10000,99999)
                    idName = myName
                    sock.sendto(str(idRand)+'|'+idName+'|'+str(sendingDistances),("127.0.0.1",int(value)))

                prevsent += UPDATE_INTERVAL

        for sock in readable: #if there's something to be read....
            # print "yo"
            # string, addr = sock.recvfrom(2048, socket.MSG_PEEK)
            # if string > 0:
            #     print "sfd"
            #     print "yaaaa"
            try:
                recvMsg = sock.recv(2048)
                print recvMsg
                recvId, recvName, recvRest = recvMsg.split('|')
                recvGraph = eval(recvRes)
                graph[recvName] = recvRest
                for key,value in recvRest.iteritems():
                    graph[key][recvName] = value
            except:
                print "disconnect detected"
                break

        for sock in err:
            print "ERROR"
        # print temp
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------


    
if __name__ == "__main__": #since packHeader and unpackHeader are exported to PingServer we only want main() to run when it actually runs
    main()

    #python2 lsr.py A 2000 Topology1\configA.txt
    #python2 open.py Topology1
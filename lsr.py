import argparse
import socket
import select
import time
import sys
import random
import errno

#global constants
UPDATE_INTERVAL = 1 #set at 1 second
ROUTE_UPDATE_INTERVAL = 30* UPDATE_INTERVAL
MINI_UPDATE_INTERVAL = 1/float(3)
MSG = 0
DESTPORT = 1
TIME = 2


BIG_NUMBER = 984653


def pathGen(start, end, dictionary, cost):
    temp = end
    pathStr = temp
    while temp != start:
        temp = dictionary[temp]
        pathStr += temp

    return "least-cost path to node " + end + " : " + pathStr[::-1] + " and the cost is " + str(round(cost,1))


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
        temp = line.rstrip('\r').split(' ')
        if len(temp) != 1:
            graph[temp[0]] = {myName : temp[1]}
            dictMap[temp[0]] = temp[2]
            graph[myName][temp[0]] = temp[1]
    print graph
    print dictMap
    sendingDistances = graph[myName]
    portDict = {}
    portAlive = {}
    forwardQueue = []
    # print str(sendingDistances)
    # test = str(sendingDistances)
    # test2 = eval(test)
    # print test2
    # print test == sendingDistances

#timing considerations
    STARTTIME = time.time()
    prevsent = STARTTIME
    tick = STARTTIME
    countThree = 0
    tenTick = tick
        #Main loop where data is sent
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
    #setting variables we'll need before the loop starts

    print "Node started..."
    while True:

        readable, writable, errors = select.select([s],[s],[s]) #using select to poll our socket to see if it is readable

        for sock in writable:#if s is writable (it should be), there are packets in the send queue AND one of the next two conditions is met:
            if forwardQueue:
                msgArr = forwardQueue.pop(0)
                sock.sendto(msgArr[MSG],("127.0.0.1",int(msgArr[DESTPORT])))


        for sock in readable: #if there's something to be read...
            while True:
                try:
                    recvMsg, addr = sock.recvfrom(2048)
                except socket.error, e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        time.sleep(.01)
                        print 'No data available'
                        break
                    else:
                        # a "real" error occurred
                        print "errno.WSAECONNRESET"
                # try:
                #     recvMsg, addr = sock.recvfrom(2048)
                # except:
                #     # print "ugly disconnect detected" + str(addr[1]) + recvMsg
                #     break
                for key, value in dictMap.iteritems():
                    # print value, int(addr[1])
                    if int(value) == int(addr[1]):
                        portAlive[addr[1]] = time.time()
                recvId, recvName, recvRest = recvMsg.split('|')
                if recvId == 'PING':
                    # print 'PING'
                    continue
                if recvId not in portDict: #if we haven't seen this LSP before
                    portDict[recvId] = [recvMsg, recvName, time.time()]
                    for key,value in dictMap.iteritems():
                        if key != recvName: #don't want to send same packet back to original sender
                            forwardQueue.append([recvMsg, value])

                    recvGraph = eval(recvRest)
                    graph[recvName] = recvGraph
                    for key,value in recvGraph.iteritems():
                        if key in graph:
                            graph[key][recvName] = value
                        else:
                            graph[key] = {recvName : value}


        for sock in errors:
            print "ERROR"



        if time.time() - MINI_UPDATE_INTERVAL > prevsent: #once a second
            # print time.time() - STARTTIME
            if countThree == 0:
                for key,value in dictMap.iteritems():
                    idRand = random.randint(0,99999)
                    idName = myName
                    # forwardQueue.append([(str(idRand)+'|'+idName+'|'+str(sendingDistances).strip(' ')),value])

                for timeSent, blarg in portDict.iteritems():#gets rid of all entries more than a second old every second
                    if timeSent < time.time() - UPDATE_INTERVAL:
                        del portDict[timeSent]

                for key, value in portAlive.iteritems():
                    print key, str(time.time() - float(value)), value

                print "___________________"
            else:
                for key,value in dictMap.iteritems():
                    forwardQueue.append([('PING'+ '|'+idName+'|'+str(time.time())),value])






            countThree = (countThree+1)%3
            prevsent += MINI_UPDATE_INTERVAL


        if time.time() - 30*UPDATE_INTERVAL > tenTick: # once every 30 seconds
            print "dijijijikstra time" 
            # for key, value in sorted(graph.items()):
                # print key, sorted(graph[key].items())
            tenTick += 30*UPDATE_INTERVAL
            vQueue = []
            distDict = {}
            prevDict = {}
            for key, value in graph.iteritems(): # I need to come up wiht names other than key, value
                vQueue.append(key)
                distDict[key] = BIG_NUMBER
                prevDict[key] = None
            print "I am: " + myName
            distDict[myName] = 0
            prevDict[myName] = myName

            while vQueue:
                #shortest = min(distDict, key=distDict.get)
                shortest = min([x for x in distDict.keys() if x in vQueue], key=lambda y: distDict[y]) #this line is disguisting
                vQueue.remove(shortest)

                for key, value in graph[shortest].iteritems():
                    lengthCheck = distDict[shortest] + float(graph[shortest][key])
                    if lengthCheck < distDict[key]:
                        distDict[key] = lengthCheck
                        prevDict[key] = shortest

            # print distDict
            # print prevDict
            for letter in sorted(distDict.keys()):
                if letter != myName:
                    print pathGen(myName, letter, prevDict, distDict[letter])
            print "______________________________________________________________________"
            # break
        # print temp
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------


    
if __name__ == "__main__": #since packHeader and unpackHeader are exported to PingServer we only want main() to run when it actually runs
    main()

    #python2 lsr.py A 2000 Topology1\configA.txt
    #python2 open.py Topology1
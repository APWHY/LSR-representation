import argparse
import os
import multiprocessing

def worker(letter, port,filename):
    os.system(str('start /WAIT cmd  /k python2 lsr.py ' + letter + ' ' + port + ' ' + filename))

def main():
    #doing parsing of args
    parser = argparse.ArgumentParser()
    parser.add_argument("folderName", help= "the name of the folder with all the configs")
    args = parser.parse_args()

    loc = os.getcwd() + '\\' + args.folderName
    fileTxt = []
    print loc

    for file in os.listdir(loc):
        f = open( str(loc+'\\'+file),'rb')
        fileTxt = fileTxt + f.read().split('\n')
        f.close()


    print fileTxt
    scriptList = {}
    for line in fileTxt:
        temp = line.split(' ')
        if len(temp) != 1:
            scriptList[temp[0]] = temp[2]

    print scriptList
    jobs = []
    for key, value in scriptList.iteritems():

        p = multiprocessing.Process(target=worker, args=(key, value, str(args.folderName+ '\\config'+key+'.txt')))
        jobs.append(p)
        p.start()

        #os.system(str('start /WAIT cmd  /k python2 lsr.py ' + key + ' ' + value + ' ' + args.folderName+ '\\config'+key+'.txt'))




if __name__ == '__main__':

    main()

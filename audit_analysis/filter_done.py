import os
import sys
import re
import datetime

data = {}

def getSec(tm):
    buf = tm.split(':')
    a = int(buf[0])*3600+int(buf[1])*60+int(buf[2])
    return a
def noDone(tm, user, cmd):
    if not data.has_key(user):
        data[user] = [cmd, tm] #create
    elif data[user][0] == 'done':
        if cmd != 'done':
            data[user] = [cmd, tm] #update: new cmd
    else:
        if cmd != 'done':
            print 'No done', data[user][1], user, data[user][0]
        data[user] = [cmd, tm]   #update: 1,get done.2,no done

def filterByUser(tm, user, cmd):
    if not data.has_key(user):
        data[user] = [cmd, tm] #create
    elif data[user][0] == 'done':
        if cmd != 'done':
            data[user] = [cmd, tm] #update: new cmd
    else:
        if cmd != 'done':
            print 'No done', data[user][1], user, data[user][0]
        else:
            interval = getSec(tm) - getSec(data[user][1])
            print 'case', interval, 's ', data[user][1], user, data[user][0]
        data[user] = [cmd, tm]   #update: 1,get done.2,no done
            
def filterByCmd(tm, user, cmd):
    if not data.has_key(user):
        data[user] = [cmd, tm] #create
    elif data[user][0] == 'done':
        if cmd != 'done':
            data[user] = [cmd, tm] #update: new cmd
    else:
        if cmd != 'done':
            print 'No done', data[user][1], user, data[user][0]
        else:
            interval = getSec(tm) - getSec(data[user][1])
            print 'case', interval, 's ', data[user][1], user, data[user][0]
        data[user] = [cmd, tm]   #update: 1,get done.2,no done
            
            
def filterByOperation(fileName, flag):
    if (flag == 1):
        print 'Start filter the cmds that no done'
    elif (flag == 2):
        print 'Input the user'
        user = raw_input('--->')   #python2 is raw_input. python3 is input
        print 'Start filter the cmd by user[', user, ']'
    elif (flag == 3):
        print 'Input the cmd'
        cmd = raw_input('--->')
        print 'Start filter the cmd[', cmd, ']'
    else:
        print 'mode is unknow'
        exit(1)
    f = open(fileName)
    buf = f.readline()
    if buf == '':
        print 'Can access this file'
        exit(1) 
    while (1):
        buf = f.readline()
        if buf == '':
            break
        tempTime = re.findall(r"::(.+?)\.", buf)
        tempUser = re.findall(r"audit user: (.+?) ", buf)
        tempCommand = re.findall(r"CLI (.+?)\n", buf)
        if len(tempTime) == 0 or len(tempUser) == 0 or len(tempCommand) == 0:
            #print 'No correct info'
            continue
        if tempCommand[0] == "'startup'" or tempCommand[0] == "'exit'":#startup and exit is no done
            #print 'No correct info'
            continue
        if tempCommand[0] == 'aborted':#abort is the same as done
            tempCommand[0] = 'done'
        #tempSec = getSec(tempTime[0])
    #    print tempTime, tempUser, tempCommand
        if (flag == 1):
            noDone(tempTime[0], tempUser[0], tempCommand[0])
        elif (flag == 2):
            if (tempUser[0].find(user) >= 0):
                filterByUser(tempTime[0], tempUser[0], tempCommand[0])
                #data[tempUser[0]] = [tempCommand[0], tempTime[0]] 
        elif (flag == 3):
            if (tempCommand[0].find(cmd) >= 0) or (tempCommand[0] == 'done'):
                filterByCmd(tempTime[0], tempUser[0], tempCommand[0])
                #data[tempUser[0]] = [tempCommand[0], tempTime[0]] 
    for kv in data.items():
        if kv[1][0] != 'done':
            print 'No done', kv[1][1], kv[0], kv[1][0]
    

if len(sys.argv) != 2:
    print 'Error Paramters'
    exit(1)

fileName = sys.argv[1]


if os.access(fileName, os.F_OK) == False:
    print 'File is not exist'
    exit(1)
print 'Input:'
print '1: filter the cmd is no done'
print '2: filter by user'
print '3: filter by cmd'

flag = int(input('--->'))
filterByOperation(fileName, flag)

import os
import sys
import re
import datetime

#start define
patch1 = '.upgrade.patch'
patch2 = '.patch'
patch3 = 'confd_dyncfg.patch'
hopeYang = 'hope.yang'
#end define

change=[]
nowConfdDyncfgYang=[]
hopeConfdDyncfgYang=[]

def getModifyLines(str):
    all =  re.findall(r'\b\d+\b', str)
    if len(all) < 4:
        print 'Error'
        exit(1)
    delLines = int(all[1])
    addLines = int(all[3])
    print 'delLines', delLines, 'addLines', addLines
    return delLines, addLines

#load the upgrade patch
def loadUpgradePatch(path):
    count = 0
    delLines = 0
    addLines = 0
    f = open(path, 'r')
    for i in range(2): #jump the header
        f.readline()
    while (1):
        buf = f.readline()
        if buf == '':
            if count != 0:
                change.append(tmp)  #save the last one
               
            break
        if buf[0] == '@':
            # save the object to list and new a object
            if count != 0:
                change.append(tmp)
            count += 1
            tmp = [[], []]
            # get the change line number
            delLines, addLines = getModifyLines(buf)
            delLines -= 3 #cut the last 3 lines.
            addLines -= 3
            continue

        elif buf[0] == '-':
            buf = buf[1:]
            tmp[0].append(buf)

        elif buf[0] == '+':
            buf = buf[1:]
            tmp[1].append(buf)

        else:
            #save this line to object
            buf = buf[1:]
            if delLines > len(tmp[0]):
                tmp[0].append(buf)
            if addLines > len(tmp[1]):
                tmp[1].append(buf)

    print 'Load ', count ,' changes OK'
    f.close()

#load the now confd_dyncfg.yang
def loadNowYang(path):
    f = open(path, 'r')
    while (1):
        buf = f.readline()
        if buf == '':
            break
        nowConfdDyncfgYang.append(buf)

def compare(change, num):
    for i in range(0, len(change)):
        if change[i] != nowConfdDyncfgYang[num+i]:
            return -1

    return 0

def saveNewConfdDyncfgYang():
    f = open(hopeYang, 'w')
    for i in range(0, len(hopeConfdDyncfgYang)):
        f.write(hopeConfdDyncfgYang[i])
    f.close()
    print 'Save the end yang(hope.yang)'

def mergePatchToNowYang():
    start = 0
    for i in range(0, len(change)):
        for j in range(start, len(nowConfdDyncfgYang)):
            if (len(change[i][0]) + j) <= len(nowConfdDyncfgYang):
                #compare
                ret = compare(change[i][0], j)
                if ret == 0:
                    #save the new
                    print 'Match change', i
                    start = j + len(change[i][0])
                    for n in range(0, len(change[i][1])):
                        hopeConfdDyncfgYang.append(change[i][1][n])
                    
                    break
                else:
                    #save this line
                    hopeConfdDyncfgYang.append(nowConfdDyncfgYang[j])
                    start = j + 1
                    if start >= len(nowConfdDyncfgYang):
                        print 'compare change ', i, ' end the old yang file'
                        exit(1)
    #save the end of old yang file
    for i in range(start, len(nowConfdDyncfgYang)):
        hopeConfdDyncfgYang.append(nowConfdDyncfgYang[i])

    saveNewConfdDyncfgYang()

#Add a title and modify the files name
def sortPatchFormat(patchName, fileName):
    data = []
    year = str(datetime.datetime.now().year)
    data.append('/*\n')
    data.append(' * Copyright (c) '+year+' Ericsson AB.\n')
    data.append(' * All rights reserved.\n')
    data.append(' */\n')
    data.append('\n')
    
    f = open(patchName, 'r')
    buf = f.readline()
    line1 = buf.replace(fileName, 'confd_dyncfg.yang', 1)
    data.append(line1)
    buf = f.readline()
    line2 = buf.replace(hopeYang, 'confd_dyncfg.yang', 1)
    data.append(line2)
    while (1):
        buf = f.readline()
        if buf == '':
            break
        data.append(buf)
    f.close()

    f = open(patch3, 'w')
    for i in range(0, len(data)):
        f.write(data[i])

    f.close()
     

################ start ########################
if len(sys.argv) != 4:
    print 'Error Paramters'
    print '\n'
    print 'Example:'
    print '    python cgp_tool.py [file1] [file2] [file3] '
    print ''
    print '      file1 is the confd_dyncfg.yang of current CONFD'
    print '      file2 is the confd_dyncfg.yang of upgrade CONFD'
    print '      file3 is the confd_dyncfg.yang from our code after build (integration/obj/vipp-vrp/opt/confd_build/yang/confd_dyncfg.yang)'
    print ''
    exit(1)

old = sys.argv[1]
new = sys.argv[2]
now = sys.argv[3]
#verify the args
if os.access(old, os.F_OK) == False:
    print 'File1 is not exist'
    exit(1)

if os.access(new, os.F_OK) == False:
    print 'File2 is not exist'
    exit(1)

if os.access(now, os.F_OK) == False:
    print 'File3 is not exist'
    exit(1)

#generate the patch
os.system('diff -up '+ old + ' ' + new + ' > ' + patch1) #need .upgrade.patch when exit.
loadUpgradePatch(patch1)
loadNowYang(now)
mergePatchToNowYang()
cmd = 'diff -up ' + new + ' ' + hopeYang +' > ' + patch2
os.system(cmd)
print 'Run', cmd, 'to get the patch'
sortPatchFormat(patch2, new)
os.remove(patch1)
os.remove(patch2)
print 'Generate confd_dyncfg.yang and you need copy it to (integration/comp/confd/model)'

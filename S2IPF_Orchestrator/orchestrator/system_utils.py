#!/usr/bin/python
# coding=utf-8
#   _________________ .________________________
#  /   _____/\_____  \|   \______   \_   _____/
#  \_____  \  /  ____/|   ||     ___/|    __)
#  /        \/       \|   ||    |    |     \
# /_______  /\_______ \___||____|    \___  /
#         \/         \/                  \/
# ________                .__                     __                 __
# \_____  \_______   ____ |  |__   ____   _______/  |_____________ _/  |_  ___________
#  /   |   \_  __ \_/ ___\|  |  \_/ __ \ /  ___/\   __\_  __ \__  \\   __\/  _ \_  __ \
# /    |    \  | \/\  \___|   Y  \  ___/ \___ \  |  |  |  | \// __ \|  | (  <_> )  | \/
# \_______  /__|    \___  >___|  /\___  >____  > |__|  |__|  (____  /__|  \____/|__|
#         \/            \/     \/     \/     \/                   \/
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# author : Esquis Benjamin for CSGroup
#


import subprocess
import exceptions
import sys

global PROCESS_ID_FIELD
PROCESS_ID_FIELD = 1

global FATHER_PROCESS_ID_FIELD
FATHER_PROCESS_ID_FIELD = 2

import signal


# signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# exception definition
class DiskSpaceUsedException(Exception):

    def __init__(self, strMsg):
        self._strMsg = strMsg

    def __str__(self):
        return 'DiskSpaceUsedException : %s' % (str(self._strMsg))


class MemoryUsedByProcessException(Exception):

    def __init__(self, strMsg):
        self._strMsg = strMsg

    def __str__(self):
        return 'MemoryUsedByProcessException: %s' % (str(self._strMsg))


# Fonction permettant de connaitre la taille d'un repertoire, le resultat est exprime en M octets  
def diskSpaceUsed(workingDirectory):
    resultInMoctets = 0

    try:
        p = subprocess.Popen("/usr/bin/du -sk %s" % workingDirectory, shell=True, stdout=subprocess.PIPE)
        out = p.stdout.read()
        resultInKoctets = out.split()
        p.wait()
        resultInMoctets = float(resultInKoctets[0]) / 1024.0

    except Exception, e:
        strError = str(e).split("\n")
        raise DiskSpaceUsedException(strError[0])

    return resultInMoctets


# Fonction permettant de connaitre la memoire utilisee par un processus et ses sous-processus associes, le resultat est exprime en M octets
def memoryUsedByProcessAndChildrenProcesses(idProcess):
    tot_mem_Mo_sum = 0

    try:
        # On va recuperer la liste des sous process du process que l'on veut etudier
        processList = obtainSubProcessesFromMainProcess(idProcess)
        tot_mem_Mo_sum = 0

        for procNum in processList:
            tot_mem_tmp = memoryUsedByProcess2(procNum)
            tot_mem_Mo_sum += tot_mem_tmp

    except Exception, e:
        strError = str(e).split("\n")
        raise MemoryUsedByProcessException(strError[0])

    return tot_mem_Mo_sum


# Fonction permettant de connaitre la memoire utilisee par un processus et ses sous-processus associes, le resultat est exprime en M octets
def memoryUsedByChildrenProcesses(idProcess):
    tot_mem_Mo_sum = 0

    try:
        # On va recuperer la liste des sous process du process que l'on veut etudier
        processList = obtainSubProcessesFromMainProcess(idProcess)
        tot_mem_Mo_sum = 0

        for procNum in processList:
            if (procNum != idProcess):
                tot_mem_tmp = memoryUsedByProcess2(procNum)
                tot_mem_Mo_sum += tot_mem_tmp

    except Exception, e:
        strError = str(e).split("\n")
        raise MemoryUsedByProcessException(strError[0])

    return tot_mem_Mo_sum


# Fonction permettant de connaitre la memoire utilisee par un processus, le resultat est exprime en M octets
def memoryUsedByProcess(idProcess):
    file_name = '/proc/' + str(idProcess) + '/maps'

    try:
        fd = open(file_name)
        tot_mem = 0

        for l in fd:
            flds = l.split()

            # All malloc()ed memory goes into anonymous memory blocks.
            # Hence I am considering only anonymous memory chunks, which will have only 5 columns in the output.
            if len(flds) > 5: continue
            mem_start, mem_end = flds[0].split('-')
            mem_start = int('0x' + mem_start, 16)
            mem_end = int('0x' + mem_end, 16)
            tot_mem = tot_mem + mem_end - mem_start
        fd.close()

        tot_mem_Ko = tot_mem / 1024.0
        tot_mem_Mo = tot_mem_Ko / 1024.0

    except Exception:
        # Si on a rencontre un probleme pour lire les donnees de memoire
        # Alors on renvoie un resultat nul
        tot_mem_Mo = 0

    return tot_mem_Mo


def memoryUsedByProcess2(idProcess):
    _scale = {'kB': 1024.0, 'mB': 1024.0 * 1024.0,
              'KB': 1024.0, 'MB': 1024.0 * 1024.0}

    try:
        statFile = open("/proc/" + str(idProcess) + "/status")
        statInfo = statFile.read()
        statFile.close
        i = statInfo.index("VmHWM:")
        lstHWM = statInfo[i:].split(None, 3)
        if (len(lstHWM) < 3):
            tot_mem_Mo = 0  # error bad formatting
        else:
            tot_mem_Mo = float(float(lstHWM[1]) * _scale[lstHWM[2]])
    except Exception:
        tot_mem_Mo = 0

    return tot_mem_Mo / (1024.0 * 1024.0)


def elapsedTime(idProcess, pov):
    p = subprocess.Popen("/bin/ps jhS %s" % idProcess, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read()
    elements = out.split()
    p.wait()
    return elements[pov]


class UserElapsedTimeException(object):
    pass


def userElapsedTime(idProcess):
    res = ""
    try:
        res = elapsedTime(idProcess, 8)
    except Exception, e:
        strError = str(e).split("\n")
        raise UserElapsedTimeException(strError[0])
    return res


def returnChildIDs(tabProcess, idProcess):
    childsList = []
    for proc in tabProcess:
        currentProcessID = int(proc[PROCESS_ID_FIELD])
        currentFatherProcessID = int(proc[FATHER_PROCESS_ID_FIELD])
        if (currentFatherProcessID == idProcess):
            childsList.append(currentProcessID)
    return childsList


def modifyList(argsFinal, currentProcessList, idProcess):
    childsList = returnChildIDs(argsFinal, idProcess)
    currentProcessList = childsList + currentProcessList

    return currentProcessList


def obtainSubProcessesFromMainProcess(idProcess):
    argsFinal = []
    finalProcessList = []
    p = subprocess.Popen("ps -ef | grep " + str(idProcess), shell=True, stdout=subprocess.PIPE)
    out = p.communicate()[0]
    args = out.split("\n")
    # On recupere les processus dans un tableau
    for i in range(len(args) - 1):
        argsFinal.append(args[i].split())

    # On enleve la premiere ligne
    argsFinal.pop(0)

    # Tant que l'on trouve des fils, on continue
    currentProcessList = []
    currentProcessList.append(idProcess)

    while (len(currentProcessList) != 0):
        currentID = currentProcessList.pop(0)
        finalProcessList.append(currentID)
        currentProcessList = modifyList(argsFinal, currentProcessList, currentID)

    return finalProcessList


def usage():
    print "Usage: %s pid" % sys.argv[0]
    print "Get the memory usage of the given pid and child"
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    pid = int(sys.argv[1])
    print str(memoryUsedByProcessAndChildrenProcesses(pid))
    sys.exit(0)

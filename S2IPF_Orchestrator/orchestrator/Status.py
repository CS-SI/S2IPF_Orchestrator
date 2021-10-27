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


class Status(object):
    def __init__(self, pool_id=0, name="GHOST", pid=0, task_id=0, begin_time="00:00:00.0", ellapsed_time="0", ram=0,
                 status="NORUN", exitcode=666):
        self._array = [pool_id, name, pid, task_id, begin_time, ellapsed_time, ram, status, exitcode]
        self._pool_id = 0
        self._name = 1
        self._pid = 2
        self._task_id = 3
        self._begin_time = 4
        self._ellapsed_time = 5
        self._ram = 6
        self._status = 7
        self._exitcode = 8

    def to_array(self):
        return self._array

    def update(self, pool_id=None, name=None, pid=None, task_id=None, begin_time=None, ellapsed_time=None, ram=None,
               status=None, exitcode=None):
        if pool_id is not None:
            self._array[self._pool_id] = pool_id
        if name is not None:
            self._array[self._name] = name
        if pid is not None:
            self._array[self._pid] = pid
        if task_id is not None:
            self._array[self._task_id] = task_id
        if begin_time is not None:
            self._array[self._begin_time] = begin_time
        if ellapsed_time is not None:
            self._array[self._ellapsed_time] = ellapsed_time
        if ram is not None:
            if ram > self._array[self._ram]:
                self._array[self._ram] = ram
        if status is not None:
            self._array[self._status] = status
        if exitcode is not None:
            self._array[self._exitcode] = exitcode


def init_status_tasktable(the_task_table, skipped_pools):
    number_of_pools = min(int(the_task_table.List_of_Pools.count), len(the_task_table.List_of_Pools.Pool))
    # global status
    status = []
    for index in range(number_of_pools):
        current_pool = the_task_table.List_of_Pools.Pool[index]
        number_of_tasks = current_pool.List_of_Tasks.count
        status.append([])
        for subindex in range(int(current_pool.List_of_Tasks.count)):
            task = current_pool.List_of_Tasks.Task[subindex]
            tmp_status = Status(pool_id=index + 1, name=task.Name, task_id=subindex + 1)
            if index < skipped_pools:
                tmp_status = Status(pool_id=index + 1, name=task.Name, task_id=subindex + 1, status="SKIPPED",
                                    exitcode=0)
            status[index].append(tmp_status)

    return status


def init_status_pool(the_task_list, a_pool_id):
    status = []
    for subindex in range(len(the_task_list)):
        task = the_task_list[subindex]
        tmp_status = Status(pool_id=a_pool_id + 1, name=task.Name, task_id=subindex + 1, status="SCHEDULED")
        status.append(tmp_status)

    return status


def export_status(statusdict):
    out_status = []
    for p in range(len(statusdict)):
        out_status.append([])
        for t in range(len(statusdict[p])):
            out_status[p].append(statusdict[p][t].to_array())

    return out_status

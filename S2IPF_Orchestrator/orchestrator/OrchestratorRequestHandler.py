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
import os
import sys
from multiprocessing import Process, Queue
from Queue import Empty
from TaskTableReader import parse
from Scheduler import process_tasktable
import logging


def get_validation_schema_from_filename(filename):
    with open(filename, "r") as fh:
        for line in fh.readlines():
            schema_def = 'xsi:noNamespaceSchemaLocation='
            if schema_def in line:
                fragment = line[line.find(schema_def) + len(schema_def):]
                return fragment.split(fragment[0])[1]
    return None


def handler(signum, frame):
    print 'Signal handler called with signal ', signum
    sys.exit()


def task_starter(param, job_queue, res_queue):
    log = logging.getLogger("Orchestrator")
    tasktable_filename = param["filename"]
    log.info("Reading TaskTable: %s" % tasktable_filename)
    if not os.path.exists(param["filename"]):
        log.error("File %s does not exist !!" % tasktable_filename)
    else:
        schema_candidate = os.path.dirname(tasktable_filename) + os.sep + get_validation_schema_from_filename(
            tasktable_filename)
        log.info("Schema Candidate : %s" % schema_candidate)
        if not schema_candidate:
            schema_candidate = "../tests/TaskTable_L0c.xsd"
        else:
            if not os.path.exists(schema_candidate):
                schema_candidate = "../tests/" + schema_candidate

        # method to construct the Tasktable
        task_table_object_model = parse(tasktable_filename, silence=True)
        # Get the Tasktable path:
        the_filepath = os.path.dirname(tasktable_filename)
        log.info("Path of the Tasktable: " + the_filepath)
        # todo do we know all the inputs before trying to run the chain ?
        # valid_tasktable = validate_tasktable(TaskTableObjectModel, schema_candidate, the_filepath)
        # assert valid_tasktable ?

        print param
        context_file = None
        if 'context' in param and param['context'] is not None:
            context_file = param['context']
        skipped_pool = 0
        if 'skip' in param and param['skip'] is not None:
            skipped_pool = param['skip']

        process_tasktable(task_table_object_model, the_filepath, context_file, skipped_pool, job_queue, res_queue)

        log.info("Keep going...")


def the_end():
    log = logging.getLogger("Orchestrator")
    log.info("This is not the End...")


class OrchestratorRequestHandler(object):
    def __init__(self):
        self.log = logging.getLogger("Orchestrator")
        self._p = Process()
        self._status = []
        self._child_job_queue = Queue()
        self._child_res_queue = Queue()

    def start(self, x):
        # empty status list
        while not self._child_res_queue.empty():
            self._status = self._child_res_queue.get()
        self.log.info("Starting...")
        if self._p.is_alive():
            self.log.info("A task is already launched")
        else:
            # flush queue before relaunching
            while not self._child_job_queue.empty():
                self._child_job_queue.get()
            while not self._child_res_queue.empty():
                self._child_res_queue.get()
            self._p = Process(target=task_starter, args=(x, self._child_job_queue, self._child_res_queue,))
            self._p.start()
            self.log.info("Task handling process launched under pid " + str(self._p.pid))
        the_end()
        return True

    def status(self, x):
        # empty status list
        while not self._child_res_queue.empty():
            self._status = self._child_res_queue.get()
        if self._p.is_alive():
            self._child_job_queue.put('STATUS')
            try:
                self._status = self._child_res_queue.get(timeout=0.5)
            except Empty:
                pass
        return self._status

    def stop(self, x):
        return self.kill()

    def pause(self, x):
        if self._p.is_alive():
            self.log.info("Pausing Orchestrator ")
            self._child_job_queue.put('PAUSE')
        else:
            self.log.info("Nothing to pause")
        return True

    def resume(self, x):
        if self._p.is_alive():
            self.log.info("Resuming Orchestrator")
            self._child_job_queue.put('RESUME')
        else:
            self.log.info("Nothing to resume")
        return True

    def kill(self):
        self.log.info("Stoping tasktable handling process ...")
        try:
            if self._p.is_alive():
                # Empty the queue
                while not self._child_res_queue.empty():
                    self._status = self._child_res_queue.get()
                self._child_job_queue.put('ABORT')
                # self._p.terminate()
                self._p.join()
                self.log.info("Tasktable handling process stopped")
                try:
                    status = self._child_res_queue.get(timeout=0.2)
                    self._status = status
                except Empty:
                    pass
            else:
                self.log.info("Tasktable handling process is not alive")
        except Exception as e:
            self.log.error("Tasktable handling process can't be stoped")
            return False
        return True

    def is_alive(self):
        return True

    def is_processing(self):
        return self._p.is_alive()

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
import argparse
import xmlrpclib
import sys
import tabulate

import os

host = "localhost"
port = 8100
host_file = None

new_env = os.environ.copy()
if "IDPORCH_PORT" in new_env:
    port = int(new_env["IDPORCH_PORT"])

connection_string = 'http://' + host + ':' + str(port)
s = xmlrpclib.ServerProxy(connection_string, allow_none=True)

try:
    alive = s.is_alive()
except:
    print "%s is not available." % connection_string
    sys.exit(0)


def pretty_print(statuslist):
    headers = ["Pool", "Name", "Pid", "Task_id", "begin_time", "Time", "RAM", "Status ", "ExitCode"]
    statuses = []
    for p in range(len(statuslist)):
        for t in range(len(statuslist[p])):
            statuses.append(statuslist[p][t])
    print tabulate.tabulate(statuses, headers)


def start(args):
    s.start(args)


def status(args):
    print ("Execution status: ")
    print pretty_print(s.status(args))


def status_service(args):
    is_processing = s.is_processing()
    if is_processing:
        print ("Orchestrator is PROCESSING")
    else:
        print ("Orchestrator is IDLE")


def stop(args):
    print "Stopping orchestrator processing"
    result = s.stop(args)
    if result:
        print "Processing stopped"
    else:
        print "Enable to stop the current processing"


def pause(args):
    s.pause(args)
    print "Orchestrator paused"


def resume(args):
    s.resume(args)
    print "Orchestrator resumed"


def start_service(args):
    print "Start orchestrator service"


def stop_service(args):
    print "Stop orchestrator service"
    res = s.stopall()
    if res:
        print "Orchestrator successfully stopped."
    else:
        print "Enable to stop the orchestrator cleanly."
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description='Manage orchestrator',  # main description for help
        epilog='Beta')  # displayed after help
    subparsers = parser.add_subparsers()

    parser_start = subparsers.add_parser('start', help="Start Orchestrator")
    parser_start.add_argument('filename', metavar="FILENAME")
    parser_start.add_argument('--skip', type=int, required=False)
    parser_start.add_argument('--context', type=str, required=False)
    parser_start.set_defaults(func=start)

    parser_status = subparsers.add_parser('status', help="Orchestrator status")
    parser_status.set_defaults(func=status)

    parser_stop = subparsers.add_parser('stop', help="Stop Orchestrator")
    parser_stop.add_argument('-id', type=int, required=True)
    parser_stop.set_defaults(func=stop)

    parser_stop = subparsers.add_parser('pause', help="Pause Orchestrator")
    parser_stop.set_defaults(func=pause)

    parser_stop = subparsers.add_parser('resume', help="Resume Orchestrator")
    parser_stop.set_defaults(func=resume)

    parser_start_service = subparsers.add_parser('service', help="Orchestrator service")
    moparsers = parser_start_service.add_subparsers()

    parser_start_service = moparsers.add_parser('start', help="Starts Orchestrator service")
    parser_start_service.set_defaults(func=start_service)

    parser_stop_service = moparsers.add_parser('stop', help="Starts Orchestrator service")
    parser_stop_service.set_defaults(func=stop_service)

    parser_status_service = moparsers.add_parser('status', help="Get Orchestrator status")
    parser_status_service.set_defaults(func=status_service)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

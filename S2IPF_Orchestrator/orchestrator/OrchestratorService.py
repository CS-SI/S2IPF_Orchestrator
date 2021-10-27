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
import logsetup
import sys
import signal
import functools
import logging
import errno
# import log
from OrchestratorRequestHandler import OrchestratorRequestHandler
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import json, os, datetime

host = "localhost"
port = 8100
host_file = None
timeout = 30

new_env = os.environ.copy()
if "IDPORCH_PORT" in new_env:
    port = int(new_env["IDPORCH_PORT"])

if "IDPORCH_PROCESSING_DIR" not in os.environ:
    log = logging.getLogger("Orchestrator")
    log.error("Var IDPORCH_PROCESSING_DIR is requested to run the Orchestrator")
    sys.exit(errno.EINVAL)


def stopall():
    logger = logging.getLogger("Orchestrator")
    logger.info("Stopping orchestrator...")
    try:
        request_handler.kill()
        server.kill()
    except Exception as e:
        logger.error("Enable to stop the orchestrator cleanly...")
        return False
    logger.info("Orchestrator stopped")
    return True


class MyServer(SimpleXMLRPCServer):
    
    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=False, encoding=None, bind_and_activate=True):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none, encoding, bind_and_activate)
        self.quit = 0

    def serve_forever(self):
        while not self.quit:
            self.handle_request()
        log = logging.getLogger("Orchestrator")
        log.info("Orchestrator XMLRPC stopped")

    def kill(self):
        self.quit = 1
        return 1


def prepare_service(a_request_handler):

    # Restrict to a particular path.
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    # Create server
    a_server = MyServer((host, port),
                        requestHandler=RequestHandler, logRequests=False)
    a_server.register_introspection_functions()
    a_server.register_instance(a_request_handler)
    a_server.register_function(stopall)

    return a_server


def run_service(a_server):
    # Run the server's main loop
    a_server.serve_forever()


# put to global scope to be able to stop them
request_handler = OrchestratorRequestHandler()
server = prepare_service(request_handler)


def main():
    try:
        logger = logging.getLogger("Orchestrator")
        logger.info('This is the beginning, running on host=' + host + " and port=" + str(port))
        run_service(server)
        logger.info('This is the END')
    except KeyboardInterrupt:
        request_handler.kill()


if __name__ == "__main__":
    main()

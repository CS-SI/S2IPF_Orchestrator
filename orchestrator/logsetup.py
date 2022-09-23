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
import logging
import os
import sys
import errno
from log_colorizer import make_colored_stream_handler

handler = make_colored_stream_handler()
log = logging.getLogger('Orchestrator')
log.setLevel(logging.INFO)
log.addHandler(handler)

if "IDPORCH_DEBUG" in os.environ:
    log.setLevel(logging.DEBUG)

if "IDPORCH_LOG_DIR" not in os.environ:
    log = logging.getLogger("Orchestrator")
    log.error("Var IDPORCH_LOG_DIR is requested to run the Orchestrator")
    sys.exit(errno.EINVAL)

try:
    fh = logging.FileHandler(os.environ["IDPORCH_LOG_DIR"] + os.sep + 'orchestrator.log')
    fh.setFormatter(logging.Formatter(
        '%(asctime)s %(process)d %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s', "%Y-%m-%d %H:%M:%S"))
    fh.setLevel(log.getEffectiveLevel())
    log.addHandler(fh)
    eh = logging.FileHandler(os.environ["IDPORCH_LOG_DIR"] + os.sep + 'orchestrator.err')
    eh.setFormatter(logging.Formatter(
        '%(asctime)s %(process)d %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s', "%Y-%m-%d %H:%M:%S"))
    eh.setLevel(logging.ERROR)
    log.addHandler(eh)
except Exception as e:
    raise Exception("Log File not found %s" % ('$IDPORCH_LOG_DIR' + os.sep + 'orchestrator.log'))

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
import StringIO


class IdpInfos(object):
    def __init__(self):
        self._listOfIDPSC = []
        self._RAM = 2

    def add_idpsc(self, idpsc):
        """
        add an IDPSC and it's version to the list
        """
        self._listOfIDPSC.append(idpsc)

    def set_ram(self, a_ram):
        """
        add an IDPSC and it's version to the list
        """
        self._RAM = a_ram

    def write_to_file(self, filepath):
        """
        Write the list of IDPSC to an xml file
        """
        output = StringIO.StringIO()
        output.write('<?xml version="1.0" ?>\n')
        output.write('<IDP_Infos xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
        output.write('xmlns:base="http://gs2.esa.int/DICO/1.0/IPF/base/">\n')
        output.write('    <Performance_Options>\n')
        output.write('        <maxSizeRAM>' + str(self._RAM) + '</maxSizeRAM>\n')
        output.write('    </Performance_Options>\n')
        i = 0
        while i < len(self._listOfIDPSC):
            tmp_idpsc = self._listOfIDPSC[i]
            if len(tmp_idpsc) == 2:
                output.write(
                    '    <IDPSc_Name version="' + str(tmp_idpsc[1]) + '" >' + str(tmp_idpsc[0]) + '</IDPSc_Name>\n')
            i += 1
        output.write('</IDP_Infos>')
        with open(filepath, "w") as fh:
            fh.write(output.getvalue())

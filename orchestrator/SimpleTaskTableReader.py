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
#  Copyright (C) 2014-2022 CS GROUP – France, https://www.csgroup.eu
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
from datetime import date

from xmltodict import parse, unparse
import xmltodict
import StringIO


class TaskTableReader(object):
    def __init__(self, schema_file_path):
        self.schema_file_path = schema_file_path

    @staticmethod
    def convert_to_dict(self, file_name):
        """
          >>> t = TaskTableReader()
          >>> r = t.convert_to_dict("../tests/TaskTable_L0c.xml")
        """
        with open(file_name, "r") as fh:
            doc = parse(fh.read())
            return doc

    @staticmethod
    def dom_to_string(self, dom_object):
        output = StringIO.StringIO()
        output.write('<?xml version="1.0" ?>\n')
        dom_object.export(
            output, 0, name_='Ipf_Task_Table',
            namespacedef_='',
            pretty_print=True)
        return output

    @staticmethod
    def joborder_dom_to_string(self, dom_object):
        output = StringIO.StringIO()
        output.write('<?xml version="1.0" ?>\n')
        dom_object.export(
            output, 0, name_='Ipf_Job_Order',
            namespacedef_='',
            pretty_print=True)
        return output

    @staticmethod
    def validate_xml(self, file_name):
        from xml.dom.minidom import parseString
        try:
            with open(file_name, "r") as fh:
                parseString(fh.read())
                return True
        except:
            return False

    def validate_with_schema(self, file_name, schema_file_name=None):
        if schema_file_name:
            sfn = schema_file_name
        else:
            sfn = self.schema_file_path

        with open(sfn, "r") as hschema:
            with open(file_name, "r") as hfile:
                from lxml import etree
                xmlschema_doc = etree.parse(hschema)
                xmlschema = etree.XMLSchema(xmlschema_doc)
                doc = etree.parse(hfile)
                return xmlschema.validate(doc)

    def write_task(self):
        pass

import StringIO
import unittest

import orchestrator
from orchestrator.TaskTableReader import parse


def dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Task_Table',
        namespacedef_='',
        pretty_print=True)
    return output


class TaskTableCreationTestCase(unittest.TestCase):
    def runTest(self):
        got_me_good = orchestrator.TaskTableReader.Ipf_Task_TableType()

        got_me_good.Version = "2.1"
        assert got_me_good.Version is "2.1"


if __name__ == '__main__':
    unittest.main()

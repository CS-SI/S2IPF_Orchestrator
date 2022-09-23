import StringIO
import unittest

from orchestrator.Scheduler import process_tasktable
from orchestrator.TaskTableReader import parse


def dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Task_Table',
        namespacedef_='',
        pretty_print=True)
    return output


class TaskTestCase(unittest.TestCase):
    def runTest(self):
        TaskTableObjectModel = parse("TaskTable_L0c.xml", silence=True)
        process_tasktable(TaskTableObjectModel, "TaskTable_L0c.xsd")


if __name__ == '__main__':
    unittest.main()

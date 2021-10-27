import StringIO
import unittest

import xmltodict

from orchestrator.JobOrderReader import *
from orchestrator.TaskTableReader import parse


def dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Task_Table',
        namespacedef_='',
        pretty_print=True)
    return output


class OpenTaskTableAlternativeTestCase(unittest.TestCase):
    def runTest(self):
        TaskTableObjectModel = parse("TaskTable_L0c.xml", silence=True)
        dict_document_2 = xmltodict.parse(dom_to_string(TaskTableObjectModel).getvalue())

        number_of_pools = int(dict_document_2["Ipf_Task_Table"]["List_of_Pools"]["@count"])
        assert number_of_pools == 5
        assert int(TaskTableObjectModel.List_of_Pools.count) == 5

        im_not_like_you = Ipf_Job_OrderType()


if __name__ == '__main__':
    unittest.main()

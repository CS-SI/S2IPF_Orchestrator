import StringIO
import unittest

import xmltodict

from orchestrator.JobOrderReader import parse


def dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Job_Order',
        namespacedef_='',
        pretty_print=True)
    return output


class OpenJobOrderAlternativeTestCase(unittest.TestCase):
    def runTest(self):
        JobOrderModel = parse("JobOrder.INIT_LOC_L0_52742.xml", silence=True)
        dict_document_2 = xmltodict.parse(dom_to_string(JobOrderModel).getvalue())

        assert dict_document_2["Ipf_Job_Order"]["Ipf_Conf"]["Version"] == "01.03"
        assert JobOrderModel.Ipf_Conf.Version == "01.03"


if __name__ == '__main__':
    unittest.main()

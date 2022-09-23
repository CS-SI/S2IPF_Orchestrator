import unittest

from xmltodict import unparse

from orchestrator import SimpleTaskTableReader


class OpenJobOrderTestCase(unittest.TestCase):
    def runTest(self):
        r = SimpleTaskTableReader.TaskTableReader("TaskTable_L0c.xsd")
        d = r.convert_to_dict("JobOrder.INIT_LOC_L0_52742.xml")
        assert d["Ipf_Job_Order"]["Ipf_Conf"]["Version"] == "01.03"
        d["Ipf_Job_Order"]["Ipf_Conf"]["Version"] = "Ordinary love"
        ordinary = unparse(d, pretty=True)
        assert "Ordinary love" in ordinary


if __name__ == '__main__':
    unittest.main()

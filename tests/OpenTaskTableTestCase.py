import unittest

from orchestrator import SimpleTaskTableReader


class OpenTaskTableTestCase(unittest.TestCase):
    def runTest(self):
        r = SimpleTaskTableReader.TaskTableReader("TaskTable_L0c.xsd")
        d = r.convert_to_dict("TaskTable_L0c.xml")
        assert d["Ipf_Task_Table"]["Version"] == "01.03"

        number_of_pools = int(d["Ipf_Task_Table"]["List_of_Pools"]["@count"])
        assert number_of_pools == 5

        number_of_tasks = int(d["Ipf_Task_Table"]["List_of_Pools"]["Pool"][0]["List_of_Tasks"]["@count"])
        assert number_of_tasks == 2


if __name__ == '__main__':
    unittest.main()

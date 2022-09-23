import os
import unittest

from orchestrator import SimpleTaskTableReader


class SchemaValidationTestCase(unittest.TestCase):
    def runTest(self):
        r = SimpleTaskTableReader.TaskTableReader("TaskTable_L0c.xsd")
        d = r.validate_with_schema("TaskTable_L0c.xml", "TaskTable_L0c.xsd")
        assert d
        for each in os.listdir("../orchestrator/tasktables"):
            res = r.validate_with_schema("../orchestrator/tasktables/" + each, "TaskTable_L0c.xsd")
            if not res:
                print "%s failed" % each


if __name__ == '__main__':
    unittest.main()

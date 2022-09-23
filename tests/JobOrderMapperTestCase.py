import unittest

from orchestrator import JobOrderMapper


class JobOrderMapperTestCase(unittest.TestCase):
    def runTest(self):
        r = JobOrderMapper.JobOrderMapper()
        r.store_as_json()


if __name__ == '__main__':
    unittest.main()

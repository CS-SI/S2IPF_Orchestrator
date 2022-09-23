import unittest

from tests.OpenJobOrderAlternativeTestCase import OpenJobOrderAlternativeTestCase
from tests.OpenJobOrderTestCase import OpenJobOrderTestCase
from tests.OpenTaskTableAlternativeTestCase import OpenTaskTableAlternativeTestCase
from tests.OpenTaskTableTestCase import OpenTaskTableTestCase
from tests.RegExpTestCase import RegExpTestCase
from tests.TaskTableCreationTestCase import TaskTableCreationTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(OpenJobOrderAlternativeTestCase())
    suite.addTest(OpenJobOrderTestCase())
    suite.addTest(OpenTaskTableAlternativeTestCase())
    suite.addTest(OpenTaskTableTestCase())
    suite.addTest(TaskTableCreationTestCase())
    suite.addTest(RegExpTestCase())
    return suite


if __name__ == '__main__':
    the_suite = suite()
    unittest.main()

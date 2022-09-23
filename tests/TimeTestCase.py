import unittest

from orchestrator.tmRetrievalPolicy import *


class TimeTestCase(unittest.TestCase):
    def runTest(self):
        file_name = "S2A_OPER_MSI_L0__DS_CGS1_20130329T000142_S20091211T165851_N01.01"

        fina2 = "S2A_OPER_AUX_S11110_CGS1_20130329T000142_V20091211165851_20091211170213_A123456_WP_LN.bin"

        print get_validity_dates_from_file(file_name)
        print get_validity_dates_from_file(fina2)


if __name__ == '__main__':
    unittest.main()

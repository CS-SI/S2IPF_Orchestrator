import unittest

from orchestrator.FileUtils import is_a_valid_filename, parse_all
from orchestrator.tmRetrievalPolicy import getLatestValIntersect, getLatestValidityClosest, getBestCenteredCover, \
    getLatestValCoverClosest, getLatestValidity, getLatestByCreationDate
from orchestrator.tmRetrievalPolicy import get_validity_dates_from_file, getValCover, getLatestValCover, \
    getValIntersect


class RetrievalPolicyTestCase(unittest.TestCase):
    def runTest(self):
        r6 = "S2A_OPER_AUX_S11110_CGS1_20130326T000142_V20091224165851_20091229165851_A123456_WP_LN.bin"
        r5 = "S2A_OPER_AUX_S11110_CGS1_20130325T000142_V20091211165851_20091214165851_A123456_WP_LN.bin"
        r4 = "S2A_OPER_AUX_S11110_CGS1_20130324T000142_V20091222165851_20091227165851_A123456_WP_LN.bin"
        r3 = "S2A_OPER_AUX_S11110_CGS1_20130323T000142_V20091213165851_20091226165851_A123456_WP_LN.bin"
        r2 = "S2A_OPER_AUX_S11110_CGS1_20130322T000142_V20091215165851_20091226165851_A123456_WP_LN.bin"
        r1 = "S2A_OPER_AUX_S11110_CGS1_20130321T000142_V20091214165851_20091218165851_A123456_WP_LN.bin"

        r0 = "S2A_OPER_GIP_BLINDP_CGS1_20121031T075922_V19830101T000000_20200101T000000_B00.xml"

        file_list = [r1, r2, r3, r4, r5, r6]

        assert is_a_valid_filename(r5)

        pf2 = parse_all(r5)

        map_props = {}
        for each in pf2:
            map_props[each[0]] = each[1]

        time_period = map_props["applicability_time_period"]

        print time_period

        begin, end = get_validity_dates_from_file(r5)

        print begin
        import datetime
        endr5 = begin + datetime.timedelta(days=3)
        print endr5.strftime("%Y%m%d%H%M%S")

        beginr3 = endr5 - datetime.timedelta(days=1)
        print beginr3.strftime("%Y%m%d%H%M%S")

        beginr2 = endr5 + datetime.timedelta(days=1)
        print beginr2.strftime("%Y%m%d%H%M%S")

        endr1 = beginr2 + datetime.timedelta(days=3)
        print endr1.strftime("%Y%m%d%H%M%S")

        beginr4 = endr1 + datetime.timedelta(days=4)
        print beginr4.strftime("%Y%m%d%H%M%S")

        beginr6 = beginr4 + datetime.timedelta(days=2)
        print beginr6.strftime("%Y%m%d%H%M%S")

        endr2 = beginr6 + datetime.timedelta(days=2)
        print endr2.strftime("%Y%m%d%H%M%S")

        endr4 = endr2 + datetime.timedelta(days=1)
        print endr4.strftime("%Y%m%d%H%M%S")

        endr6 = endr4 + datetime.timedelta(days=2)
        print endr6.strftime("%Y%m%d%H%M%S")

        t0 = beginr2 + datetime.timedelta(days=1)
        t1 = beginr4 + datetime.timedelta(days=1)

        the_result = getValCover(file_list, t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert r2 in the_result
        assert r3 in the_result
        assert len(the_result) == 2

        the_result = getLatestValCover(file_list, t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert the_result == r3

        the_result = getValIntersect(file_list, t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert r1 in the_result
        assert r2 in the_result
        assert r3 in the_result
        assert r4 in the_result
        assert len(the_result) == 4

        the_result = getLatestValIntersect(file_list, t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert r4 in the_result

        print t0 + (t1 - t0) / 2
        the_result = getLatestValidityClosest(file_list, t0, t1, datetime.timedelta(hours=6),
                                              datetime.timedelta(hours=6))
        assert r4 in the_result

        the_result = getBestCenteredCover(file_list, t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert r3 in the_result

        the_result = getLatestValCoverClosest(file_list, t0, t1, datetime.timedelta(hours=6),
                                              datetime.timedelta(hours=6))
        assert r2 in the_result

        the_result = getLatestValidity(file_list, t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert r6 in the_result

        the_result = getLatestByCreationDate(file_list, t0, t1, datetime.timedelta(hours=6),
                                             datetime.timedelta(hours=6))
        assert r6 in the_result

        the_result = getValIntersect([r0], t0, t1, datetime.timedelta(hours=6), datetime.timedelta(hours=6))
        assert r0 in the_result


if __name__ == '__main__':
    unittest.main()

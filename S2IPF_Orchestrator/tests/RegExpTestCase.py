import unittest

from orchestrator.FileUtils import is_a_valid_filename, parse_all, parse_all_as_dict
from orchestrator.GranuleTileFileUtils import is_l1a_mask, is_l1c_mask


class RegExpTestCase(unittest.TestCase):
    def list_as_map(self, the_list):
        map_props = {}
        for each in the_list:
            map_props[each[0]] = each[1]
        return map_props

    def runTest(self):
        file_name = "S2A_OPER_MSI_L0__GR_CGS1_20130329T000142_S20091211T170010_D01_N01.01"

        fina2 = "S2A_OPER_AUX_S11110_CGS1_20130329T000142_V20091211165851_20091211170213_A123456_WP_LN.bin"
        assert is_a_valid_filename(file_name)

        fina3 = "S2A_OPER_MSK_TECQUA_CGS1_20141104T134012_S20141104T134012_D03_B03_MSIL1A.gml"
        assert is_l1a_mask(fina3)

        grac = "S2A_OPER_MSK_CLOUDS_CGS3_20141104T134012_A123456_T15SWC_B03_MSIL1C.gml"
        assert is_l1c_mask(grac)

        wtfis = "S2A_OPER_MSI_L0__DS_CGS1_20140523T174055_S20091211T165851_N01.01"
        assert self.list_as_map(parse_all(wtfis))['applicability_start'] == '20091211T165851'
        assert parse_all_as_dict(wtfis)['applicability_start'] == '20091211T165851'

        pdi_ds_xml_name = "S2A_OPER_MTD_L0U_DS_CGS1_20130329T000142_S20091211T165851.xml"
        assert is_a_valid_filename(pdi_ds_xml_name)

        raw_name = "S2A_OPER_MSI_L1A_GR_CGS1_20141104T134012_S20141104T134012_D01_B01.raw"
        assert is_a_valid_filename(raw_name)

        b0name = "S2A_OPER_GIP_BLINDP_CGS1_20121031T075922_V19830101T000000_20200101T000000_B00.xml"
        assert is_a_valid_filename(b0name)


if __name__ == '__main__':
    unittest.main()

import re

def is_a_valid_atf_filename(the_file_name):
    atf = "(S2A|S2B)_ATF_(L0c|L1A|L1B)_DB([0-9]{3})_GR([0-9]{3})([0-9]{4})_GR([0-9]{3})([0-9]{4})_([0-9]{2})"
    p = re.compile(atf)
    return p.match(the_file_name)

def parse_a_valid_atf_filename(the_file_name):
    parsing_map = {}
    atf = "(S2A|S2B)_ATF_(L0c|L1A|L1B)_DB([0-9]{3})_GR([0-9]{3})([0-9]{4})_GR([0-9]{3})([0-9]{4})_([0-9]{2})"
    p = re.compile(atf)
    match = p.match(the_file_name)
    assert match
    groups = p.groups()
    parsing_map["Mission_ID"] = groups[0]
    parsing_map["Product_Level"] = groups[1]
    parsing_map["Datablock_Number"] = groups[2]
    parsing_map["First_Granule"] = groups[3]
    parsing_map["Previous_Margin"] = groups[4]
    parsing_map["Last_Granule"] = groups[5]
    parsing_map["Next_Margin"] = groups[6]
    parsing_map["Detector_Number"] = groups[7]

    return parsing_map

def is_a_valid_atf_image(the_file_name):
    atf = "PDI_ATF_ID_L(0c|1A|1B|1C)_DB([0-9]{3})_DD([0][0-9]|[1][0-2])_B([0][1-9]|[1][0-2]|8A)\.(hdr|raw|HDR|RAW)"
    p = re.compile(atf)
    return p.match(the_file_name)

def parse_a_valid_atf_image(the_file_name):
    parsing_map = {}
    atf = "PDI_ATF_ID_(L0c|L1A|L1B|L1C)_DB([0-9]{3})_DD([0][0-9]|[1][0-2])_B([0][1-9]|[1][0-2]|8A)\.(hdr|raw|HDR|RAW)"
    p = re.compile(atf)
    match = p.match(the_file_name)
    assert match
    groups = p.groups()
    parsing_map["Product_Level"] = groups[0]
    parsing_map["Datablock_Number"] = groups[1]
    parsing_map["Detector_Id"] = groups[2]
    parsing_map["Band_Number"] = groups[3]
    parsing_map["File_Extension"] = groups[4]
    return parsing_map

def is_a_valid_atf_mask(the_file_name):
    atf_mask = "PDI_ATF_ID_([A-Z|0-9|_]{10})_(MSI|L0c|L1A|L1B|L1C)_DB([0-9]{3})_DD([0][0-9]|[1][0-2])_B([0][1-9]|[1][0-2]|8A)\.(gml|GML)"
    p = re.compile(atf_mask)
    return p.match(the_file_name)

def parse_a_valid_atf_mask(the_file_name):
    parsing_map = {}
    atf_mask = "PDI_ATF_ID_([A-Z|0-9|_]{10})_(MSI|L0c|L1A|L1B|L1C)_DB([0-9]{3})_DD([0][0-9]|[1][0-2])_B([0][1-9]|[1][0-2]|8A)\.(gml|GML)"
    p = re.compile(atf_mask)
    match = p.match(the_file_name)
    assert match
    groups = p.groups()
    parsing_map["Mask_Type"] = groups[0]
    parsing_map["Product_Level"] = groups[1]
    parsing_map["Datablock_Number"] = groups[2]
    parsing_map["Detector_Id"] = groups[3]
    parsing_map["Band_Number"] = groups[4]

    return parsing_map
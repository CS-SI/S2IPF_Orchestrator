
def default_dirs():
    import os
    gipps = ["GIP_ATMIMA", "GIP_ATMSAD", "GIP_DATATI", "GIP_LREXTR", "GIP_INVLOC", "GIP_VIEDIR", "GIP_SPAMOD", "GIP_BLINDP", "GIP_CLOINV", "GIP_PRDLOC", "GIP_R2PARA", "GIP_R2SWIR", "GIP_R2EQOB", "GIP_R2EQOG", "GIP_R2DEPI", "GIP_R2DEFI", "GIP_R2WAFI", "GIP_R2DEBA", "GIP_R2L2NC", "GIP_R2DENT", "GIP_R2DECT", "GIP_R2MACO", "GIP_R2NOMO", "GIP_R2ABCA", "GIP_R2BINN", "GIP_R2CRCO", "GIP_G2PARA", "GIP_G2PARE", "GIP_EARMOD", "GIP_GEOPAR", "GIP_INTDET", "GIP_TILPAR", "GIP_RESPAR", "GIP_MASPAR", "GIP_JP2KPA", "GIP_ECMWFP", "GIP_DECOMP", "GIP_OLQCPA", "GIP_PROBAS"]

    da_map = {}
    da_map["GIP"] = "$IDPORCH_GIPP_DIR"
    da_map["PDI_DS"] = "$IDPORCH_INPUT_DATASTRIP_DIR"
    da_map["PDI_GR_LIST"] = "$IDPORCH_INPUT_GRANULES_DIR"
    da_map["PDI_DS_GR_LIST"] = "$IDPORCH_INPUT_GRANULES_DIR"
    da_map["IERS"] = "$IDPORCH_AUX_DIR/AUX_UT1UTC"
    da_map["DEM_GLOBEF"] = "$IDPORCH_AUX_DIR/DEM_GLOBEF" #todo check carefully docs (GLOBE or GLOBEF) ?
    da_map["DEM_GLOBE"] = "$IDPORCH_AUX_DIR/DEM_GLOBEF" #todo check carefully docs (GLOBE or GLOBEF) ?
    da_map["DEM_SRTM"] = "$IDPORCH_AUX_DIR/DEM_SRTM"
    da_map["ECMWF"] = "$IDPORCH_AUX_DIR/ECMWF"
    da_map["ISP_UNCOMP_LIST"] = "$IDPORCH_INPUT_DATASTRIP_DIR/IMG_DATA"
    da_map["ISP_LIST"] = "$IDPORCH_INPUT_DATASTRIP_DIR/IMG_DATA"
    da_map["ISP"] = "$IDPORCH_INPUT_DATASTRIP_DIR/IMG_DATA"
    da_map["QUICKLOOK_GEO"] = "$IDPORCH_INPUT_DATASTRIP_DIR/QL_DATA"
    da_map["PDI_SAD"] = "$IDPORCH_INPUT_DATASTRIP_DIR/ANC_DATA"
    da_map["ANC_DATA"] = "$IDPORCH_INPUT_DATASTRIP_DIR/ANC_DATA"
    da_map["AUX_UT1UTC"] = "$IDPORCH_AUX_DIR/AUX_UT1UTC"

    da_map["IDP_INFOS"] = "idp_infos.xml"

    for each in gipps:
        da_map[each] = "$IDPORCH_GIPP_DIR"

    return da_map

def parameters():
    _map = {}
    keys = ["IDPORCH_HOME", "IDPORCH_BIN_DIR", "IDPORCH_TEMP_DIR", "IDPORCH_CONFIG_DIR", "IDPORCH_PROCESSING_DIR", "IDPORCH_TDS_L0NC_DIR", "IDPORCH_TDS_L0C_DIR", "IDPORCH_TDS_L1A_DIR", "IDPORCH_TDS_L1B_DIR", "IDPORCH_TDS_L1AB_RAWEXAMPLES_DIR", "IDPSC_EXE_DIR"]
    restricted_keys = ["IDPORCH_LOG_DIR", "IDPORCH_INPUT_DATASTRIP_DIR", "IDPORCH_INPUT_GRANULES_DIR", "IDPORCH_GIPP_DIR", "IDPORCH_AUX_DIR"]

    default_map = {}
    default_map["IDPORCH_LOG_DIR"] = "/tmp"
    default_map["IDPORCH_INPUT_DATASTRIP_DIR"] = "~ipfdata/Validation_Test_Data_Set/test_data_set/NOMINAL/L0u/S2A_OPER_MSI_L0U_DS_CGS1_20130329T000142_S20091211T165851_N01.01"
    default_map["IDPORCH_INPUT_GRANULES_DIR"] = "~ipfdata/Validation_Test_Data_Set/test_data_set/NOMINAL/L0u"
    default_map["IDPORCH_GIPP_DIR"] = "/data/TDS_v1_2_CS/GIPP"
    default_map["IDPORCH_AUX_DIR"] = "~sharasse/S2IPF/S2IPF-Val/s2ipf_validation/test_data_set/TDS_CONF/AUX_FILES"

    bigmap = {}
    bigmap["mandatory"] = restricted_keys
    bigmap["optional"] = keys
    bigmap["default"] = default_map

    _map["TaskTable_L0c"] = bigmap
    return _map

def store_dates():
    import json
    sensing_time = ("1983-01-01T00:00:00Z","2020-01-01T00:00:00Z")
    with open("orchestratorSensingTime.json", "w") as fh:
        json.dump(sensing_time, fh, sort_keys=True, indent=4, separators=(',', ': '))

def store_default_dirs():
    import json
    with open("DB.json", "w") as fh:
        json.dump(default_dirs(), fh, sort_keys=True, indent=4, separators=(',', ': '))

def store_parameters():
    import json
    with open("orchestratorEnviron.json", "w") as fh:
        json.dump(parameters(), fh, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    store_default_dirs()
    store_dates()
    store_parameters()
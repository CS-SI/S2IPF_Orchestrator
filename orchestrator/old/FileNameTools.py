
def createParallelInfoStr(parameters):
    out_str = ""
    if ("DATABLOCK_NUMBER" in parameters ):
        out_str += "_DB"+parameters["DATABLOCK_NUMBER"]
    
    if "PARALLEL_BAND" in parameters:
        if parameters["PARALLEL_BAND"] == True:
            out_str += "_"+parameters["PARALLEL_BAND_IDENT"]
            
    if "PARALLEL_BAND_QL" in parameters:
        if parameters["PARALLEL_BAND_QL"] == True:
            out_str += "_"+parameters["PARALLEL_BAND_QL_IDENT"]
    
    if "PARALLEL_DETECTOR" in parameters:
        if parameters["PARALLEL_DETECTOR"] == True:
            out_str += "_"+parameters["PARALLEL_DETECTOR_IDENT"]
    elif "PARALLEL_DETECTOR_IDENT" in parameters:
        out_str += "_"+parameters["PARALLEL_DETECTOR_IDENT"]
        
    if "PARALLEL_ATF" in parameters:
        if parameters["PARALLEL_ATF"] == True:
            out_str += "_"+parameters["PARALLEL_ATF_DETECTOR_IDENT"]
            out_str += "_"+parameters["PARALLEL_ATF_BEGIN_GRANULE"]+"_"+parameters["PARALLEL_ATF_BEGIN_MARGIN"]
            out_str += "_"+parameters["PARALLEL_ATF_END_GRANULE"]+"_"+parameters["PARALLEL_ATF_END_MARGIN"]+"_"
    
    if "PARALLEL_GRANULE" in parameters:
        if parameters["PARALLEL_GRANULE"] == True:
            out_str += "_"+parameters["PARALLEL_GRANULE_DETECTOR_IDENT"]
            out_str += "_"+parameters["PARALLEL_GRANULE_BEGIN_GRANULE"]
            out_str += "_"+parameters["PARALLEL_GRANULE_END_GRANULE"]
    
    if "PARALLEL_TILE" in parameters:
        if parameters["PARALLEL_TILE"] == True:
            out_str += "_"+parameters["PARALLEL_TILE_IDENT"]
            
            




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

def store_default_dirs():
    import json
    with open("DB.json", "w") as fh:
        json.dump(default_dirs(), fh)

def directory_mapper(extension, the_map=default_dirs(), raise_if_missing=True):
    #todo directory_mapper is now dynamic, it changes at each pool iteration...
    target_extension = extension

    if target_extension in the_map.keys():
       return the_map[target_extension]
    else:
        if raise_if_missing:
            raise Exception("Unknown file type %s" % target_extension)
        return None
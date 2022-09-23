import os
from orchestrator.FileUtils import is_a_valid_filename

def getDefaultValidator(parameters, the_type):
    return True

def getPDI_DS(parameters, the_type):
    if the_type == "Directory":
        #we must look for xml file inside...
        result = [each for each in os.listdir(parameters[0]) if is_a_valid_filename(each)]
        if result:
            return True
    else:
        result = [each for each in parameters if is_a_valid_filename(each)]
        if result:
            return True
    return False

def getPDI_GR_LIST(parameters, the_type):
    assert the_type == "Directory"
    result = [each for each in os.listdir(parameters[0]) if each.startswith("DB")]
    if not result:
        return False

    for eachdb in result:
        db_content = [each for each in os.listdir(parameters[0] + os.sep + eachdb) if is_a_valid_filename(each)]
        if not db_content:
            return False
        for db_dir in db_content:
            tested_dir = parameters[0] + os.sep + eachdb + os.sep + db_dir + os.sep + "IMG_DATA"
            if not os.path.exists(tested_dir):
                return False

    return True

def getQUICKLOOK_GEO(parameters, the_type):
    assert the_type == "Directory"
    result = [each for each in os.listdir(parbameters[0]) if each.startswith("DB")]
    if not result:
        return False
    return True

def getPDI_DS_GR_LIST(parameters, the_type):
    assert the_type == "Directory"
    result = [each for each in os.listdir(parameters[0]) if each.startswith("DB")]
    if not result:
        return False

    for eachdb in result:
        db_content = [each for each in os.listdir(parameters[0] + os.sep + eachdb) if is_a_valid_filename(each)]
        if not db_content:
            return False
        for db_dir in db_content:
            tested_dir = parameters[0] + os.sep + eachdb + os.sep + db_dir
            metadatas = [each for each in os.listdir(tested_dir) if is_a_valid_filename(each)]
            if not metadatas:
                return False

    return True

def getPDI_ATF_LIST(parameters, the_type):
    assert the_type == "Directory"
    result = [each for each in os.listdir(parameters[0]) if each.startswith("DB")]
    if not result:
        return False

    for eachdb in result:
        db_content = [each for each in os.listdir(parameters[0] + os.sep + eachdb) if is_a_valid_filename(each)]
        if not db_content:
            return False
        for db_dir in db_content:
            tested_dir = parameters[0] + os.sep + eachdb + os.sep + db_dir + os.sep + "IMG_DATA"
            if not os.path.exists(tested_dir):
                return False

    return True

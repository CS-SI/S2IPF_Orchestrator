# coding=utf-8
#   _________________ .________________________
#  /   _____/\_____  \|   \______   \_   _____/
#  \_____  \  /  ____/|   ||     ___/|    __)
#  /        \/       \|   ||    |    |     \
# /_______  /\_______ \___||____|    \___  /
#         \/         \/                  \/
# ________                .__                     __                 __
# \_____  \_______   ____ |  |__   ____   _______/  |_____________ _/  |_  ___________
#  /   |   \_  __ \_/ ___\|  |  \_/ __ \ /  ___/\   __\_  __ \__  \\   __\/  _ \_  __ \
# /    |    \  | \/\  \___|   Y  \  ___/ \___ \  |  |  |  | \// __ \|  | (  <_> )  | \/
# \_______  /__|    \___  >___|  /\___  >____  > |__|  |__|  (____  /__|  \____/|__|
#         \/            \/     \/     \/     \/                   \/
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# author : Esquis Benjamin for CSGroup
#
import logging
import datetime
from tmRetrievalPolicy import get_utc_date_from_utc_string
from FileUtils import fully_resolve
from FileUtils import folder_fusion
import os
from JobOrderReader import InputType, List_of_File_NamesType
import shutil


# prepare the inputs for a task
def prepare_inputs_olqc(a_task, a_task_id, context_info, task_dir):
    log = logging.getLogger("Orchestrator")
    log.info("Preparing inputs for task " + a_task.Name + " number " + str(a_task_id + 1))

    working_dir = task_dir + os.sep + "input"
    try:
        os.mkdir(working_dir)
    except OSError as exception:
        if not os.path.exists(working_dir):
            raise

    inputs_map = resolve_inputs_OLQC(a_task.List_of_Inputs.Input, a_task.Name, a_task_id, context_info, working_dir)
    return inputs_map


# resolve the inputs for a task
def resolve_inputs_OLQC(inputs_list, a_task_name, a_task_id, context_info, working_dir):
    log = logging.getLogger("Orchestrator")
    nb_instance = 1
    if "OLQC_Instances" in context_info["Config"] and a_task_name.startswith("OLQC_GR"):
        nb_instance = int(context_info["Config"]["OLQC_Instances"])

    logging.info("Resolving OLQC inputs for task "+a_task_name+", id: "+str(a_task_id) + " / "+str(nb_instance))
    resolved_inputs_map = {}

    log.debug("Input length: %s" % len(inputs_list))
    for subindex in range(len(inputs_list)):
        the_format = inputs_list[subindex].List_of_Alternatives.Alternative.File_Type
        the_type = inputs_list[subindex].List_of_Alternatives.Alternative.File_Name_Type
        the_origin = inputs_list[subindex].List_of_Alternatives.Alternative.Origin
        tol0 = datetime.timedelta(seconds=inputs_list[subindex].List_of_Alternatives.Alternative.T0)
        tol1 = datetime.timedelta(seconds=inputs_list[subindex].List_of_Alternatives.Alternative.T1)
        begin = get_utc_date_from_utc_string(context_info["Sensing"][0])
        end = get_utc_date_from_utc_string(context_info["Sensing"][1])

        log.debug("OLQC: Working with Input type %s, FFormat %s, Origin %s" % (the_format, the_type, the_origin))
        # input type creation
        the_input_type = InputType(the_format, the_type)
        # resolved inputs list
        resolved_inputs = []
        alternatives = []
        name_list = List_of_File_NamesType()
        base_dir = None

        if the_origin == "DB":
            if the_type == "Directory":
                if the_format == "PDI_SAFE":
                    if a_task_name == "OLQC_DS":
                        ds_dir = fully_resolve(context_info["DB"]["PDI_DS"])
                        for d in os.listdir(ds_dir):
                            the_ds_input_dir = working_dir + os.sep + d
                            if not os.path.exists(the_ds_input_dir):
                                try:
                                    os.mkdir(the_ds_input_dir)
                                    for el in os.listdir(ds_dir + os.sep + d):
                                        if el != "QI_DATA":
                                            os.symlink(ds_dir + os.sep + d + os.sep + el,
                                                       the_ds_input_dir + os.sep + el)
                                        else:
                                            shutil.copytree(ds_dir + os.sep + d + os.sep + el,
                                                            the_ds_input_dir + os.sep + el)
                                except OSError:
                                    if not os.path.exists(the_ds_input_dir):
                                        log.error("Internal error with file: " + the_ds_input_dir)
                            resolved_inputs.append(the_ds_input_dir)
                    elif a_task_name == "OLQC_GR":
                        gr_index = 0
                        gr_dir = fully_resolve(context_info["DB"]["PDI_DS_GR_LIST"])
                        db_list = [each for each in os.listdir(gr_dir) if each.startswith("DB")]
                        for db in db_list:
                            db_content = os.listdir(gr_dir + os.sep + db)
                            for gr in db_content:
                                if gr_index % nb_instance == a_task_id:
                                    the_gr_input_dir = working_dir + os.sep + gr
                                    if not os.path.exists(the_gr_input_dir):
                                        try:
                                            os.mkdir(the_gr_input_dir)
                                            for d in os.listdir(gr_dir + os.sep + db + os.sep + gr):
                                                if d != "QI_DATA":
                                                    os.symlink(gr_dir + os.sep + db + os.sep + gr + os.sep + d,
                                                               the_gr_input_dir + os.sep + d)
                                                else:
                                                    shutil.copytree(gr_dir + os.sep + db + os.sep + gr + os.sep + d,
                                                                    the_gr_input_dir + os.sep + d)
                                        except OSError:
                                            if not os.path.exists(the_gr_input_dir):
                                                log.error("Internal error with file: " + the_gr_input_dir)
                                    resolved_inputs.append(the_gr_input_dir)
                                gr_index += 1
                    elif a_task_name == "OLQC_TILE":
                        tile_index = 0
                        tile_dir = fully_resolve(context_info["DB"]["PDI_DS_TILE_LIST"])
                        log.info("Tile directory: " + tile_dir)
                        tile_content = os.listdir(tile_dir)
                        for ti in tile_content:
                            if tile_index % nb_instance == a_task_id:
                                log.info("Treating tile " + ti)
                                the_tile_input_dir = working_dir + os.sep + ti
                                if not os.path.exists(the_tile_input_dir):
                                    try:
                                        os.mkdir(the_tile_input_dir)
                                        for d in os.listdir(tile_dir + os.sep + ti):
                                            log.info("Treating file " + d)
                                            if d != "QI_DATA":
                                                os.symlink(tile_dir + os.sep + ti + os.sep + d,
                                                           the_tile_input_dir + os.sep + d)
                                            else:
                                                shutil.copytree(tile_dir + os.sep + ti + os.sep + d,
                                                                the_tile_input_dir + os.sep + d)
                                    except OSError:
                                        if not os.path.exists(the_tile_input_dir):
                                            log.error("Internal error with file: " + the_tile_input_dir)
                                        raise
                                resolved_inputs.append(the_tile_input_dir)
                            tile_index += 1
                    else:
                        raise Exception("OLQC task type " + a_task_name + " not supported for DB PDI_SAFE input")
                else:
                    the_dir = fully_resolve(context_info["DB"][the_format])
                    alternatives.append(the_dir)
            if the_type == "Physical":
                the_dir = fully_resolve(context_info["DB"][the_format])
                dir_content = os.listdir(the_dir)
                base_dir = the_dir
                if "GIP" in the_format:
                    dir_content = filter(lambda x: the_format in x, dir_content)
                    # retrieval_Mode = inputs_list[subindex].List_of_Alternatives.Alternative.Retrieval_Mode
                    # if hasattr(Policies, "get" + retrieval_Mode):
                    #    method = getattr(Policies, "get" + retrieval_Mode)
                    #    
                    # if not method:
                    #    raise Exception("Filtering criteria %s not found !" % retrieval_Mode)
                    #
                    # filtered = method(dir_content, begin, end, tol0, tol1)
                    # alternatives.extend(filtered)
                    alternatives.extend(dir_content)
                    if len(dir_content) == 0:
                        raise Exception("No GIPP found for type %s !" % the_format)
                else:
                    alternatives.extend(dir_content)

        if the_origin == "PROC":
            keys = [each for each in context_info.keys() if "PROC." in each]
            log.debug("Asking for previous result of %s !!" % the_format)
            # PDI_SAFE exception
            if the_format == "PDI_SAFE":
                datastrip_search_key = "PROC.PDI_DS"
                granule_search_key = "PROC.PDI_DS_GR_LIST"
                granule_image_search_key = "PROC.PDI_GR_LIST"
                tile_search_key = "PROC.PDI_DS_TILE_LIST"
                if a_task_name == "OLQC_DS_L1A" or a_task_name == "OLQC_GR_L1A":
                    datastrip_search_key = "PROC.L1A.PDI_DS"
                    granule_search_key = "PROC.L1A.PDI_DS_GR_LIST"
                    granule_image_search_key = "PROC.L1A.PDI_GR_LIST"
                elif a_task_name == "OLQC_DS_L1B" or a_task_name == "OLQC_GR_L1B":
                    datastrip_search_key = "PROC.L1B.PDI_DS"
                    granule_search_key = "PROC.L1B.PDI_DS_GR_LIST"
                    granule_image_search_key = "PROC.L1B.PDI_GR_LIST"
                elif a_task_name == "OLQC_DS_L1C" or a_task_name == "OLQC_TILE_L1C":
                    datastrip_search_key = "PROC.L1C.PDI_DS"
                    tile_search_key = "PROC.L1C.PDI_DS_TILE_LIST"
                elif a_task_name == "OLQC_DS_L0" or a_task_name == "OLQC_GR_L0":
                    datastrip_search_key = "PROC.L0C.PDI_DS"
                    granule_search_key = "PROC.L0C.PDI_DS_GR_LIST"
                else:
                    raise Exception("OLQC task type " + a_task_name + " not supported for PROC PDI_SAFE input")

                if a_task_name.startswith("OLQC_DS"):
                    if datastrip_search_key in keys:
                        ds_dir = context_info[datastrip_search_key][0]
                        log.debug("Datastrip dir " + ds_dir)
                        for d in os.listdir(ds_dir):
                            the_ds_input_dir = working_dir + os.sep + d
                            if not os.path.exists(the_ds_input_dir):
                                os.symlink(os.path.relpath(ds_dir + os.sep + d, working_dir), the_ds_input_dir)
                            resolved_inputs.append(the_ds_input_dir)
                    else:
                        raise Exception("No previous process furnished the file type %s" % datastrip_search_key)

                elif a_task_name.startswith("OLQC_GR"):
                    if granule_search_key in keys:
                        gr_index = 0
                        gr_dir = context_info[granule_search_key][0]
                        log.debug("Granule dir " + gr_dir)
                        db_list = [each for each in os.listdir(gr_dir) if each.startswith("DB")]
                        for db in db_list:
                            db_content = os.listdir(gr_dir + os.sep + db)
                            for gr in db_content:
                                if gr_index % nb_instance == a_task_id:
                                    the_gr_input_dir = working_dir + os.sep + gr
                                    if not os.path.exists(the_gr_input_dir):
                                        try:
                                            os.symlink(os.path.relpath(gr_dir + os.sep + db + os.sep + gr, working_dir),
                                                       the_gr_input_dir)
                                            if not os.path.exists(os.path.join(the_gr_input_dir,"QI_DATA")):
                                                os.makedirs(os.path.join(the_gr_input_dir,"QI_DATA"))
                                        except OSError:
                                            if not os.path.exists(the_gr_input_dir):
                                                log.error("Internal error with file: " + the_gr_input_dir)
                                    resolved_inputs.append(the_gr_input_dir)
                                gr_index += 1
                        if a_task_name == "OLQC_GR_L1A" or a_task_name == "OLQC_GR_L1B":
                            if granule_image_search_key in keys and a_task_id == 0:
                                gr_image_dir = context_info[granule_image_search_key][0]
                                log.debug("FOLDER FUSION ::: start")
                                folder_fusion(gr_image_dir, gr_dir)
                                log.debug("FOLDER FUSION ::: end")
                    else:
                        raise Exception("No previous process furnished the file type %s" % granule_search_key)

                elif a_task_name == "OLQC_TILE_L1C":
                    if tile_search_key in keys:
                        tile_index = 0
                        tile_dir = context_info[tile_search_key][0]
                        tile_content = os.listdir(tile_dir)
                        for ti in tile_content:
                            if tile_index % nb_instance == a_task_id:
                                the_tile_input_dir = working_dir + os.sep + ti
                                if not os.path.exists(the_tile_input_dir):
                                    try:
                                        os.symlink(os.path.relpath(tile_dir + os.sep + ti, working_dir),
                                                   the_tile_input_dir)
                                    except OSError:
                                        if not os.path.exists(the_tile_input_dir):
                                            log.error("Internal error with file: " + the_tile_input_dir)
                                resolved_inputs.append(the_tile_input_dir)
                            tile_index += 1
                        if "PROC.PVI.PDI_DS_PVI_LIST" in keys and a_task_id == 0:
                            pvi_dir = context_info["PROC.PVI.PDI_DS_PVI_LIST"][0]
                            log.debug("PVI folder " + pvi_dir)
                            log.debug("FOLDER FUSION ::: start")
                            folder_fusion(pvi_dir, tile_dir)
                            log.debug("FOLDER FUSION ::: end")
                        if "PROC.L1C.LIST.PDI_DS_TILE_LIST" in keys and a_task_id == 0:
                            ct_info_list = context_info["PROC.L1C.LIST.PDI_DS_TILE_LIST"]
                            log.debug("Found context info: %s" % ct_info_list)
                            found = False
                            for proc in ct_info_list:
                                if proc[0] == "FORMAT_IMG_L1C":
                                    tile_image_dir = proc[1][0]
                                    log.debug("L1C image folder " + tile_image_dir)
                                    log.debug("FOLDER FUSION ::: start")
                                    folder_fusion(tile_image_dir, tile_dir)
                                    log.debug("FOLDER FUSION ::: end")
                                    found = True
                            if not found:
                                raise Exception("FORMAT_IMG_L1C image folder not found")

                else:
                    raise Exception("Task " + a_task_name + " not handled in OLQC orchestrator binding")

        for each in alternatives:
            if base_dir:
                the_link_name = working_dir + os.sep + each
                the_link_target = base_dir + os.sep + each
                the_link_target = the_link_target.replace(context_info["BASE_DIR"], "../..")
            else:
                the_link_name = working_dir + os.sep + the_format
                the_link_target = each
                the_link_target = the_link_target.replace(context_info["BASE_DIR"], "../..")

            if not os.path.exists(the_link_name):
                log.debug("We should create a symlink to %s in %s" % (the_link_target, the_link_name))
                try:
                    os.symlink(the_link_target, the_link_name)
                except OSError, e:
                    log.error("Path exist: " + the_link_name)
                    if not os.path.exists(the_link_name):
                        raise
                resolved_inputs.append(the_link_name)
            else:
                resolved_inputs.append(the_link_name)

        resolved_inputs = list(set(resolved_inputs))

        name_list = List_of_File_NamesType()
        for file_name in resolved_inputs:
            name_list.add_File_Name(file_name)
        name_list.count = len(resolved_inputs)
        the_input_type.set_List_of_File_Names(name_list)

        resolved_inputs_map[the_format] = (the_input_type, resolved_inputs)

    return resolved_inputs_map

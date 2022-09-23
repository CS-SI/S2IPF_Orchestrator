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
import datetime
import subprocess
import os
from multiprocessing import Process, Manager, active_children, Queue
from Queue import Empty
import logging
import sys
import errno
import time
from conditions import pre_condition
import FrameFileReader
import TileListFileReader
from IdpInfosWriter import IdpInfos
from Scheduler_Task import run_task
from FileUtils import fully_resolve
from GriListFileReader import get_number_of_gri
from SegmentFileReader import get_number_of_virtual_atf
import system_utils
from Status import *
import Parallel
import json


def validate_tasktable(the_task_table, icd_config, abs_path):
    # todo validate if we know all the data before trying to run the tasktable
    log = logging.getLogger("Orchestrator")
    import json
    number_of_pools = int(the_task_table.List_of_Pools.count)

    # todo read cfg by default

    db = None
    orchestrator_db_key, orchestrator_db_file = read_db_cfg(the_task_table, abs_path)
    if orchestrator_db_key:
        with open(orchestrator_db_file, "r") as fh:
            db = json.load(fh)

    input_formats = db.keys()
    output_formats = []

    valid_chain = True

    for index in range(number_of_pools):
        current_pool = the_task_table.List_of_Pools.Pool[index]
        number_of_tasks = current_pool.List_of_Tasks.count
        task_list = []
        log.info("Starting pool number %s" % index)
        for subindex in range(int(current_pool.List_of_Tasks.count)):
            task_list.append(current_pool.List_of_Tasks.Task[subindex])

        # todo detect and register output formats
        step_input_formats = register_input_formats(task_list)
        step_output_formats = register_output_formats(task_list)

        if len(set(step_input_formats).difference(set(input_formats))) > 0:
            log.error("We have a serious problem at level %s !!!!!!!!!!!: %s" % (
                index, set(step_input_formats).difference(set(input_formats))))
            valid_chain = False

        input_formats.extend(step_output_formats)

    return valid_chain


def read_cfg(the_task_table, key, abs_path):
    log = logging.getLogger("Orchestrator")
    cfg_file_list = the_task_table.List_of_Cfg_Files.Cfg_File
    for index in range(len(cfg_file_list)):
        cfg_file = cfg_file_list[index]
        if cfg_file.Version:
            if key in cfg_file.Version:
                if os.path.isabs(cfg_file.File_Name):
                    if os.path.exists(cfg_file.File_Name):
                        log.info("Detected orchestrator's environment configuration file: %s" % cfg_file.File_Name)
                        return cfg_file.Version, cfg_file.File_Name
                else:
                    if os.path.exists(abs_path + os.sep + cfg_file.File_Name):
                        log.info("Detected orchestrator's environment configuration file: %s" % (
                            abs_path + os.sep + cfg_file.File_Name))
                        return cfg_file.Version, abs_path + os.sep + cfg_file.File_Name
                    else:
                        log.error(
                            "No configuration file found for " + key + " in " + abs_path + os.sep + cfg_file.File_Name)
                        sys.exit(errno.EINVAL)

    return None, None


def read_orchestrator_cfg(the_task_table, abs_path):
    return read_cfg(the_task_table, "OrchestratorEnvironment", abs_path)


def read_db_cfg(the_task_table, abs_path):
    return read_cfg(the_task_table, "OrchestratorDB", abs_path)


def read_icd_cfg(the_task_table, abs_path):
    return read_cfg(the_task_table, "OrchestratorICDparams", abs_path)


def read_config_cfg(the_task_table, abs_path):
    return read_cfg(the_task_table, "OrchestratorConfig", abs_path)


def create_context_info(the_task_table, abs_path):
    log = logging.getLogger("Orchestrator")
    log.info("Creating context info")
    context_info = {"outputs": []}

    orchestrator_cfg_key, orchestrator_cfg_file = read_orchestrator_cfg(the_task_table, abs_path)
    if orchestrator_cfg_key:
        context_info[orchestrator_cfg_key] = orchestrator_cfg_file

    orchestrator_db_key, orchestrator_db_file = read_db_cfg(the_task_table, abs_path)
    if orchestrator_db_key:
        context_info[orchestrator_db_key] = orchestrator_db_file
        with open(orchestrator_db_file, "r") as fh:
            db = json.load(fh)
            context_info["DB"] = db

    orchestrator_config_key, orchestrator_config_file = read_config_cfg(the_task_table, abs_path)
    if orchestrator_config_key:
        context_info[orchestrator_config_key] = orchestrator_config_file
        with open(orchestrator_config_file, "r") as fh:
            config = json.load(fh)
            context_info["Config"] = config
            if "Sensing" in config:
                context_info["Sensing"] = config["Sensing"]

    orchestrator_icd_key, orchestrator_icd_file = read_icd_cfg(the_task_table, abs_path)
    if orchestrator_icd_key:
        context_info[orchestrator_icd_key] = orchestrator_icd_file
        with open(orchestrator_icd_file, "r") as fh:
            icd_config = json.load(fh)
            icd_parameters = icd_config["PARAMETERS"]
            context_info["ICD_parameters"] = icd_parameters
            if "INPUT_OUTPUT_MAPPING" in icd_config:
                context_info["INPUT_OUTPUT_MAPPING"] = icd_config["INPUT_OUTPUT_MAPPING"]
    else:
        log.error("No ICD configuration parameter file given")
        sys.exit(errno.EINVAL)

    return context_info


@pre_condition(
    lambda the_task_table, the_filepath, context_file, skipped_pool, job_queue, res_queue: the_task_table is not None)
def process_tasktable(the_task_table, the_filepath, context_file, skipped_pool, job_queue, res_queue):
    log = logging.getLogger("Orchestrator")
    number_of_pools = min(int(the_task_table.List_of_Pools.count), len(the_task_table.List_of_Pools.Pool))

    if context_file is not None:
        with open(context_file, 'r') as infile:
            context_info = json.load(infile)
    else:
        context_info = create_context_info(the_task_table, the_filepath)
        context_info["PROC"] = {}

    base_dir = prepare_base_directory_for_tasktable()
    context_info["BASE_DIR"] = base_dir

    # envvar preparation
    new_env = prepare_shell_environment_for_tasktable(context_info)
    os.environ["BASE_DIR"] = base_dir

    # OLQC_PERSISTENT special handling
    if "PERSISTENT_RESOURCES" in context_info["DB"]:
        persistent_dir = fully_resolve(context_info["DB"]["PERSISTENT_RESOURCES"])
        if not os.path.exists(persistent_dir):
            os.mkdir(persistent_dir)

    # VIRTUAL_SENSOR special handling
    log.info("Preparing VIRTUAL_SENSOR folder")
    virtual_dir = os.environ["IDPORCH_PROCESSING_DIR"] + os.sep + "VIRTUAL_SENSOR"
    if not os.path.exists(virtual_dir):
        os.mkdir(virtual_dir)
    log.info("VIRTUAL_SENSOR in "+virtual_dir)
    context_info["DB"]["VIRTUAL_SENSOR"] = virtual_dir
    # Homolog point handling
    homolog_dir = os.environ["IDPORCH_PROCESSING_DIR"] + os.sep + "HOMOLOG_POINTS_LIST"
    if not os.path.exists(homolog_dir):
        os.mkdir(homolog_dir)
    log.info("HOMOLOG_POINTS_LIST in " + homolog_dir)
    context_info["DB"]["HOMOLOG_POINTS_LIST"] = homolog_dir
    # Tie points
    tie_points_dir = os.environ["IDPORCH_PROCESSING_DIR"] + os.sep + "HOMOLOG_POINTS_LIST" + os.sep + "TIE_POINTS"
    if not os.path.exists(tie_points_dir):
        os.mkdir(tie_points_dir)
    log.info("TIE_POINTS in " + tie_points_dir)
    context_info["DB"]["TIE_POINTS"] = tie_points_dir
    # gcp points
    gcp_points_dir = os.environ["IDPORCH_PROCESSING_DIR"] + os.sep + "HOMOLOG_POINTS_LIST" + os.sep + "GCP_POINTS"
    if not os.path.exists(gcp_points_dir):
        os.mkdir(gcp_points_dir)
    log.info("GCP_POINTS in " + gcp_points_dir)
    context_info["DB"]["GCP_POINTS"] = gcp_points_dir

    idp_info = IdpInfos()
    idp_infos_dirname = base_dir + os.sep + "IDP_INFOS"
    context_info["PROC.IDP_INFOS"] = base_dir + os.sep + "IDP_INFOS" + os.sep + "idp_infos.xml"
    if not os.path.exists(idp_infos_dirname):
        os.mkdir(idp_infos_dirname)

    # Datablock info loading
    if "DATABLOCK_SIZE" not in context_info:
        context_info["DATABLOCK_SIZE"] = {}
        try:
            gr_dir = fully_resolve(context_info["DB"]["PDI_DS_GR_LIST"], True)
            log.info("Updating datablock size with the PDI_DS_GR_LIST input")
            db_list = [each for each in os.listdir(gr_dir) if each.startswith("DB")]
            for db in db_list:
                dir_content = os.listdir(gr_dir + os.sep + db)
                db_length = 0
                if len(dir_content) > 0:
                    gr_one = dir_content[0]
                    detector_to_search = gr_one[-10:-7]
                    type_to_search = gr_one[13:16]
                    for gr in dir_content:
                        if gr[-10:-7] == detector_to_search and gr[13:16] == type_to_search:
                            db_length += 1
                db_number = "%03d" % int(db[2:])
                context_info["DATABLOCK_SIZE"][db_number] = db_length
                log.info("Datablock size info:")
                log.info(context_info["DATABLOCK_SIZE"])
        except Exception as e:
            log.warn("No possible datablock info from PDI_DS_GR_LIST")

    # global status
    status = init_status_tasktable(the_task_table, skipped_pool)

    frame_file_updated = False
    tile_list_file_updated = False
    gri_list_file_updated = False
    seg_list_file_updated = False
    for index in range(skipped_pool, number_of_pools):

        if "PROC.FRAME_FILE" in context_info and not frame_file_updated:
            frame_file_updated = True
            if the_task_table.get_Test() == "true":
                log.info("Updating datablock size with the fake frame file")
                context_info["DATABLOCK_SIZE"] = {}
                context_info["DATABLOCK_SIZE"]["001"] = 24
                context_info["DATABLOCK_SIZE"]["002"] = 48
                context_info["DATABLOCK_SIZE"]["003"] = 72
            else:
                log.info("Updating datablock size with the frame file " + context_info["PROC.FRAME_FILE"][0])
                context_info["DATABLOCK_SIZE"] = {}
                frame_file = FrameFileReader.parse(context_info["PROC.FRAME_FILE"][0], silence=True)
                granules_number = frame_file.get_DATA_BLOCK_LIST().get_GRANULES_NUMBER()
                for db in granules_number:
                    db_number = "%03d" % db.get_data_block()
                    db_content = db.get_valueOf_()
                    context_info["DATABLOCK_SIZE"][db_number] = db_content

        if "PROC.TILE_LIST_FILE" in context_info and not tile_list_file_updated:
            tile_list_file_updated = True
            if the_task_table.get_Test() == "true":
                log.info("Updating tile number with the fake tile list file")
                context_info["DATABLOCK_SIZE"] = {}
                context_info["DATABLOCK_SIZE"]["001"] = 457
            else:
                log.info("Updating tile number with the tile list file " + context_info["PROC.TILE_LIST_FILE"][0])
                tile_file = TileListFileReader.parse(context_info["PROC.TILE_LIST_FILE"][0], silence=True)
                tile_numbers = tile_file.get_Number_Of_Tiles()
                context_info["DATABLOCK_SIZE"] = {}
                context_info["DATABLOCK_SIZE"]["001"] = tile_numbers

        if "PROC.GRI_LIST_FILE" in context_info and not gri_list_file_updated:
            gri_list_file_updated = True
            if the_task_table.get_Test() == "true":
                log.info("Updating gri number with the fake grilist file")
                context_info["GRI_SIZE"] = 457
            else:
                log.info("Updating tile number with the gri list file " + context_info["PROC.GRI_LIST_FILE"][0])
                gri_number = get_number_of_gri(context_info["PROC.GRI_LIST_FILE"][0])
                context_info["GRI_SIZE"] = gri_number

        if "PROC.SEGMENTATION_FILE" in context_info and not seg_list_file_updated:
            seg_list_file_updated = True
            if the_task_table.get_Test() == "true":
                log.info("Updating virtual atf number with the fake semgmentation file")
                context_info["SEG_SIZE"] = 7
            else:
                log.info(
                    "Updating virtual atf number with the segmentation file " + context_info["PROC.SEGMENTATION_FILE"][
                        0])
                atf_number = get_number_of_virtual_atf(context_info["PROC.SEGMENTATION_FILE"][0])
                context_info["SEG_SIZE"] = atf_number

        current_pool = the_task_table.List_of_Pools.Pool[index]
        number_of_tasks = current_pool.List_of_Tasks.count
        task_list = []
        log.info("Starting pool number %s" % index)
        for subindex in range(int(current_pool.List_of_Tasks.count)):
            task_list.append(current_pool.List_of_Tasks.Task[subindex])
            tmp_IDPSC = [current_pool.List_of_Tasks.Task[subindex].Name,
                         current_pool.List_of_Tasks.Task[subindex].Version]
            if tmp_IDPSC[0].startswith("OLQC_DS"):
                idp_info.add_idpsc(["OLQC", tmp_IDPSC[1]])
            elif not tmp_IDPSC[0].startswith("OLQC"):
                idp_info.add_idpsc(tmp_IDPSC)
        # todo detect and register output formats
        output_formats = register_output_formats(task_list)

        context_info["outputs"].extend(output_formats)

        idp_info.write_to_file(idp_infos_dirname + os.sep + "idp_infos.xml")
        try:
            run_pool(the_task_table, task_list, index, the_filepath, context_info, job_queue, res_queue, status,
                     new_env)
        except Exception as e:
            log.error("[Exiting] Something was wrong..: %s" % e)
            log.info("Finished pool...")
            sys.exit(errno.EINVAL)

        log.info("Finished pool...")


def prepare_base_directory_for_tasktable():
    log = logging.getLogger("Orchestrator")
    log.info("Prepare base directory for tasktable")
    if "IDPORCH_PROCESSING_DIR" not in os.environ:
        log.error("Var IDPORCH_PROCESSING_DIR is requested to run the Orchestrator")
        sys.exit(errno.EINVAL)

    if not os.path.exists(os.environ["IDPORCH_PROCESSING_DIR"]):
        os.mkdir(os.environ["IDPORCH_PROCESSING_DIR"])

    base_dir = os.environ["IDPORCH_PROCESSING_DIR"] + os.sep + "TaskTable_" + timestamp()
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    return base_dir


def register_output_formats(a_task_list):
    log = logging.getLogger("Orchestrator")

    output_formats = []
    # todo detect output formats
    for a_task in a_task_list:
        outputs = a_task.List_of_Outputs
        if len(outputs.Output) != int(outputs.count):
            log.warning("Inconsistent outputs length")

        for subindex in range(len(outputs.Output)):
            output_formats.append(outputs.Output[subindex].Type)

    return output_formats


def register_input_formats(a_task_list):
    log = logging.getLogger("Orchestrator")

    input_formats = []

    for a_task in a_task_list:
        inputs = a_task.List_of_Inputs
        if len(inputs.Input) != int(inputs.count):
            log.warning("Inconsistent input length")

        for subindex in range(len(inputs.Input)):
            input_formats.append(inputs.Input[subindex].List_of_Alternatives.Alternative.File_Type)

    return input_formats


# Pool Stuff
def run_pool(the_task_table, the_list_of_tasks, pool_id, the_filename, context_info, job_queue, res_queue, status,
             new_env):
    """
    The tasks in a pool should run in parallel
    """
    log = logging.getLogger("Orchestrator")

    # Shared context between tasks (really needed ?)
    manager = Manager()
    shared_context = manager.dict()
    shared_context.update(context_info)
    shared_context_pool = manager.dict()
    shared_context_pool.update(context_info)
    # Execution statuses
    failed = False
    paused = False
    number_of_pools = int(the_task_table.List_of_Pools.count)
    # Maximum parallel tasks (23 default)
    max_task = 23
    slots = range(max_task)
    if "Config" in context_info:
        if "CPU_RANGE" in context_info["Config"]:
            min_cpu = context_info["Config"]["CPU_RANGE"][0]
            max_cpu = context_info["Config"]["CPU_RANGE"][1]
            slots = range(min_cpu - 1, max_cpu)
        elif "MAX_TASK" in context_info["Config"]:
            max_task = int(context_info["Config"]["MAX_TASK"])
            # Slots stack
            slots = range(max_task)
    if len(slots) == 0:
        raise Exception("Wrong configuration in number of tasks to launch, check orchestratorConfig")

    # List of task
    task_list = Parallel.create_tasklist(the_task_table, the_list_of_tasks, context_info)
    # update status for the pool
    pool_status = init_status_pool(task_list, pool_id)
    status[pool_id] = pool_status
    # Task launch information
    task_left = len(task_list)
    task_to_process = min(max_task, task_left)
    task_to_launch = len(task_list)
    task_launched = 0
    max_time = the_task_table.get_Max_Time()
    # Main loop for task launch
    processes = []
    while task_left != 0 and not paused:
        start_time = datetime.datetime.now()
        tmp_time = datetime.time(start_time.hour, start_time.minute, start_time.second)
        if task_to_process != 0 and not paused:
            log.info("Task to launch in batch: " + str(task_to_process))
            for t in range(task_to_process):
                child_job_queue = Queue()
                task = task_list[task_launched + t]
                slot = slots.pop()
                p = Process(target=run_task, args=(
                    the_task_table, task, task_launched + t, shared_context, shared_context_pool, child_job_queue, slot, new_env,))
                p.start()
                log.info("Launching task " + task.Name + " under pid " + str(p.pid))
                task_status = pool_status[task_launched + t]
                task_status.update(status="RUNNING", begin_time=str(tmp_time), pid=p.pid)
                processes.append([p, task_launched + t, child_job_queue, start_time, slot])

            # update on task schedule
            task_to_launch -= task_to_process
            task_launched += task_to_process
            task_to_process = 0

        # poll on process
        for p in processes:
            task_status = pool_status[p[1]]
            time_inter = (datetime.datetime.now() - p[3])
            task_status.update(ellapsed_time=str(time_inter.seconds))
            if p[0].is_alive():
                ram = int(system_utils.memoryUsedByChildrenProcesses(p[0].pid))
                task_status.update(ram=ram)
            else:
                if p[0].exitcode >= 128:
                    task_status.update(status="ERROR", exitcode=p[0].exitcode)
                    failed = True
                else:
                    task_status.update(status="FINISHED", exitcode=p[0].exitcode)
                slots.append(p[4])
                processes.remove(p)
                task_to_process += 1
                task_left -= 1
                task_to_process = min(task_to_launch, task_to_process)
        # Job request handling
        try:
            job = job_queue.get(timeout=0.1)
            # pausing task : not launching next tasks
            if job == 'PAUSE':
                if task_to_launch > 0:
                    paused = True
                    pool_status[task_launched + 1].update(status="PAUSED")
                    log.info("Pool PAUSED")
                elif pool_id != number_of_pools - 1:
                    paused = True
                    status[pool_id + 1][0].update(status="PAUSED")
                    log.info("Pool PAUSED")
                else:
                    log.info("No pool to PAUSE")
            # resuming task
            elif job == 'RESUME' and paused == True:
                if task_to_launch > 0:
                    paused = False
                    pool_status[task_launched + 1].update(status="SCHEDULED")
                    log.info("Pool RESUMED")
                elif pool_id != number_of_pools - 1:
                    status[pool_id + 1][0].update(status="NORUN")
                    paused = False
                    log.info("Pool RESUMED")
            elif job == 'ABORT':
                # first send poison pills to child
                for p in processes:
                    task_status = pool_status[p[1]]
                    if p[0].is_alive():
                        p[2].put("ABORT")
                        task_status.update(status="ABORTED")
                # Sleep shortly to let time for child to quit
                time.sleep(2)
                counttoextinction = 0
                while len(active_children()) != 1 and counttoextinction < 2:
                    time.sleep(2)
                    counttoextinction += 1
                # then check for still not dead after the poison pill
                for p in processes:
                    if p[0].is_alive():
                        p[0].terminate()
                        log.info("Process " + str(p[0].pid) + " killed")
                        p[0].join()
                log.info("Pool ABORTED")
                # Put one last status
                res_queue.put(export_status(status))
                raise Exception("User aborted processing ...")
            elif job == 'STATUS':
                res_queue.put(export_status(status))
        except Empty:
            pass

    # Put one last status
    res_queue.put(export_status(status))
    # Something wrong
    if failed:
        raise Exception("run_pool: A task has been wrong")

    # update from pool context
    context_info.update(shared_context_pool)

    # Write the current context in json format in tmp folder
    json_dict = context_info["BASE_DIR"] + os.sep + "CurrentState_" + str(pool_id) + ".json"
    with open(json_dict, 'w') as outfile:
        new_dict = dict(context_info)
        if 'PREVIOUS.TASK.OUTPUT' in new_dict:
            del new_dict['PREVIOUS.TASK.OUTPUT']
        if 'PREVIOUS.TASK.INPUT' in new_dict:
            del new_dict['PREVIOUS.TASK.INPUT']
        json.dump(new_dict, outfile)

    log.info("End of Pool " + str(pool_id))


# Import shell env from JSON
def prepare_shell_environment_for_tasktable(context_info):
    log = logging.getLogger("Orchestrator")

    the_json_cfg_full_path = None
    new_env = os.environ.copy()

    if "OrchestratorEnvironment" in context_info:
        the_json_cfg_full_path = context_info["OrchestratorEnvironment"]
    else:
        log.error("[Quitting] : No environment loaded in the Tasktable !")
        sys.exit(1)

    log.info("Reading orchestrator cfg from %s" % the_json_cfg_full_path)

    import json
    with open(the_json_cfg_full_path) as fh:
        the_map = json.load(fh)
        for each in the_map[the_map.keys()[0]]["mandatory"]:
            if each not in new_env:
                if each in the_map[the_map.keys()[0]]["default"]:
                    new_env[str(each)] = str(
                        the_map[the_map.keys()[0]]["default"][each])  # the conversion to str fixes unicode problems
                    if not os.path.exists(os.path.expanduser(os.path.expandvars(new_env[each]))):
                        log.error("[Quitting] : %s does not exist: %s" % (each, os.path.expandvars(new_env[each])))
                        sys.exit()
                    os.environ[each] = os.path.expanduser(os.path.expandvars(new_env[each]))
                    log.info("Using value from cfg file: %s, %s" % (each, new_env[each]))
                    if not os.path.exists(os.path.expanduser(os.path.expandvars(new_env[each]))):
                        log.error("[Quitting] : %s does not exist: %s" % (each, os.path.expandvars(new_env[each])))
                        sys.exit()
                else:
                    log.error("[Quitting] : environment variable %s MUST be defined !!" % each)
                    sys.exit()
            else:
                if not os.path.exists(os.path.expanduser(os.path.expandvars(new_env[each]))):
                    log.error("[Quitting] : [%s] : %s MUST exist !" % (each, new_env[each]))
                    sys.exit()

        for each in the_map[the_map.keys()[0]]["optional"]:
            if each not in new_env:
                log.warning("maybe %s should be defined !!" % each)
            else:
                if not os.path.exists(os.path.expanduser(os.path.expandvars(new_env[each]))):
                    log.warning("maybe %s should exist !" % new_env[each])

    return new_env


# Launching procedure for a task
@pre_condition(lambda cmd, out_name, err_name, myenv: out_name is not None)
@pre_condition(lambda cmd, out_name, err_name, myenv: err_name is not None)
def run_and_capture_outputs(cmd, out_name, err_name, myenv=None):
    if myenv is None:
        myenv = os.environ.copy()
    log = logging.getLogger("Orchestrator")
    with open(out_name, "w") as fhout:
        with open(err_name, "w") as fherr:
            p = subprocess.Popen(cmd, stdout=fhout, stderr=fherr, env=myenv)
            results = [p.communicate()]
            return p.returncode


@pre_condition(lambda cmd, myenv: cmd is not None)
def run_and_capture_outputs_with_pipe(cmd, myenv=None):
    if myenv is None:
        myenv = os.environ.copy()
    log = logging.getLogger("Orchestrator")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=myenv)
    results = [p.communicate()]
    log.info(str(results))
    return results


def timestamp():
    import time
    ati = time.localtime()
    stamp = "%4d%02d%02dT%02d%02d%02d" % (ati[0], ati[1], ati[2], ati[3], ati[4], ati[5])
    return stamp

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
import traceback
from contextlib import contextmanager
import logging
import subprocess
import os
import sys
import errno
import signal
import time
from Queue import Empty
from JobOrderReader import InputType, List_of_File_NamesType
from JobOrderReader import OutputType
from Scheduler_Job import create_joborder
import TileListFileReader
from FileUtils import fully_resolve
from FileUtils import extract_task_name
from tmRetrievalPolicy import get_utc_date_from_utc_string
import datetime
import OLQCBind


@contextmanager
def log_running_task(task_name):
    log = logging.getLogger("Orchestrator")
    log.info("Starting task: %s" % os.path.expandvars(task_name))
    yield
    log.info("Finished task %s" % os.path.expandvars(task_name))


def analyze_global_parameters(a_task_table):
    log = logging.getLogger("Orchestrator")

    global_params = {}

    global_task_parameters = a_task_table.List_of_Dyn_ProcParam
    for index in range(len(global_task_parameters.Dyn_ProcParam)):
        global_params[global_task_parameters.Dyn_ProcParam[index].Param_Name[0]] = global_task_parameters.Dyn_ProcParam[
            index].Param_Default
    return global_params


def analyze_task_parameters(a_task, a_global_params, context_info):
    log = logging.getLogger("Orchestrator")

    tmp_params = {}
    local_params = {}

    options_list = a_task.List_of_Options.Option
    for subindex in range(len(options_list)):
        current_option = options_list[subindex]
        tmp_params[current_option.Name] = current_option.Value

    icd_parameters = context_info["ICD_parameters"]

    if extract_task_name(a_task.Name) in icd_parameters.keys():
        task_parameters = icd_parameters[extract_task_name(a_task.Name)]
        for t in range(len(task_parameters)):
            task_param = task_parameters[t]
            if task_param[0] in tmp_params:
                local_params[task_param[0]] = tmp_params[task_param[0]]
            elif task_param[0] in a_global_params:
                local_params[task_param[0]] = a_global_params[task_param[0]]
            else:
                local_params[task_param[0]] = task_param[1]
            log.debug("Task param for " + a_task.Name + " " + task_param[0] + " value " + local_params[task_param[0]])

    if "COMMON" in icd_parameters.keys():
        common_parameters = icd_parameters["COMMON"]
        for t in range(len(common_parameters)):
            task_param = common_parameters[t]
            if task_param[0] in tmp_params:
                local_params[task_param[0]] = tmp_params[task_param[0]]
            elif task_param[0] in a_global_params:
                local_params[task_param[0]] = a_global_params[task_param[0]]
            else:
                local_params[task_param[0]] = task_param[1]
            log.debug("Task param for " + a_task.Name + " " + task_param[0] + " value " + local_params[task_param[0]])

    return local_params


def get_running_parameters(the_task_table, a_task, context_info):
    log = logging.getLogger("Orchestrator")
    global_params = analyze_global_parameters(the_task_table)
    local_params = analyze_task_parameters(a_task, global_params, context_info)

    if "PARALLEL_TILE_IDENT" in local_params:
        if len(local_params["PARALLEL_TILE_IDENT"].split("-")) > 1:
            pass
        else:
            try:
                tile_int = int(local_params["PARALLEL_TILE_IDENT"])
            except ValueError:
                tile_id = local_params["PARALLEL_TILE_IDENT"]
                if the_task_table.get_Test() != "true":
                    tile_file = TileListFileReader.parse(context_info["PROC.TILE_LIST_FILE"][0], silence=True)
                    for t in tile_file.get_List_Tile_Id():
                        # t = TileListFileReader.List_Tile_IdType()
                        if tile_id in t.get_Tile_Id():
                            tile_int = int(t.get_Tile_Number())
                            local_params["PARALLEL_TILE_IDENT"] = '%03d' % tile_int

    return local_params


# Main task launching function
def run_task(the_task_table, a_task, a_task_id, context_info, job_queue, slot, new_env):
    log = logging.getLogger("Orchestrator")
    # Global try
    try:
        # Get OLQC passthrough
        if ("IDPORCH_NO_OLQC" in new_env or "IDPORCH_NO_FORMAT" in new_env) and a_task.Name.startswith("OLQC"):
            log.warning("OLQC task cancelled")
            sys.exit(0)

        # FORMAT L1 passthrough
        if "IDPORCH_NO_FORMAT" in new_env and a_task.Name.startswith("FORMAT_") and (
            "L1" in a_task.Name or "PVI" in a_task.Name):
            if a_task.Name.startswith("FORMAT_METADATA_DS_L1B"):
                log.info("Formatting")
            else:
                log.warning("Formatting task cancelled")
                sys.exit(0)

        # Init env vars
        # new_env = prepare_shell_environment_for_task(a_Task, context_info)
        # Create task dir
        task_dir = prepare_base_directory_for_task(a_task, context_info)
        # prepare input dirs/links
        if a_task.Name.startswith("OLQC"):
            input_map = OLQCBind.prepare_inputs_olqc(a_task, a_task_id, context_info, task_dir)
        else:
            input_map = prepare_inputs(a_task, context_info, task_dir)
        # prepare output dirs
        output_map = prepare_outputs(a_task, context_info, task_dir)
        # task_dir = prepare_execution_environment_for_task(a_Task, context_info)
        # Get the task running parameters
        running_parameters = get_running_parameters(the_task_table, a_task, context_info)

        job_order_content = create_joborder(the_task_table, a_task, context_info, running_parameters, input_map,
                                            output_map, task_dir)
        job_order_filename = task_dir + os.sep + "JobOrder_" + a_task.Name + "_" + str(os.getpid()) + ".xml"
        with open(job_order_filename, "w") as fh:
            fh.write(job_order_content)
            log.info("JobOrder writed in " + job_order_filename)

        errcode = 0
        full_path = os.path.expanduser(os.path.expandvars(a_task.File_Name))
        with log_running_task("Checking %s %s" % (full_path, job_order_filename)):
            log.info("Checking %s %s" % (full_path, job_order_filename))
            if not (os.path.exists(full_path)) and the_task_table.get_Test() == "false":
                log.error("Task script not found: [%s]" % full_path)
                sys.exit(errno.ENOENT + 128)
            out_name = task_dir + os.sep + a_task.Name + "_" + str(os.getpid()) + ".log"
            err_name = task_dir + os.sep + a_task.Name + "_" + str(os.getpid()) + ".err"
            with open(out_name, "w") as fhout:
                with open(err_name, "w") as fherr:
                    log.info("Launching " + os.path.expandvars(a_task.File_Name))
                    if the_task_table.get_Test() == "false":
                        p = subprocess.Popen([os.path.expandvars(a_task.File_Name), job_order_filename], stdout=fhout,
                                             stderr=fherr, env=new_env)
                    else:
                        p = subprocess.Popen(["date"], stdout=fhout, stderr=fherr, env=new_env)
                    while p.poll() is None:
                        try:
                            job = job_queue.get(timeout=0.1)
                            log.info("Job to do: " + job)
                            if job == "ABORT":
                                log.info("Aborting task JobOrder_" + a_task.Name + "_" + str(
                                    os.getpid()) + ".xml with SIGINT")
                                p.send_signal(signal.SIGINT)
                                counttoextinction = 5
                                while counttoextinction != 0 and p.poll() is None:
                                    time.sleep(1)
                                    counttoextinction -= 1
                                if p.poll() is None:
                                    log.info("Aborting task JobOrder_" + a_task.Name + "_" + str(
                                        os.getpid()) + ".xml with SIGTERM")
                                    p.send_signal(signal.SIGTERM)
                                    p.wait()
                        except Empty:
                            pass

                    errcode = p.returncode
    except Exception, e:
        log.error("[Exiting] Something was wrong in runtask: %s" % e)
        log.error(traceback.format_exc())
        log.info("Finished task...")
        sys.exit(errno.EINVAL + 128)

    if errcode != 0:
        # todo if is a critical process we should stop
        log.error("%s has an error code of %s" % (job_order_filename, errcode))
        if not a_task.Critical:
            sys.exit(0)
    else:
        log.info("%s has an exit code of %s" % (job_order_filename, errcode))

    sys.exit(errcode)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def alternative_processor(an_alternative, context_info, task_name):
    log = logging.getLogger("Orchestrator")

    alternatives = []

    the_format = an_alternative.File_Type
    the_type = an_alternative.File_Name_Type  # directory, file, etc
    tol0 = datetime.timedelta(seconds=an_alternative.T0)
    tol1 = datetime.timedelta(seconds=an_alternative.T1)

    origin = an_alternative.Origin

    begin = get_utc_date_from_utc_string(context_info["Sensing"][0])
    end = get_utc_date_from_utc_string(context_info["Sensing"][1])

    base_dir = None
    method = None
    # no more format validation : to be done directly in the IDPSC
    #    validator = None
    #    if hasattr(Validation, "get" + the_format):
    #        validator = getattr(Validation, "get" + the_format)
    #    else:
    #        validator = getattr(Validation, "getDefaultValidator")

    if origin == "DB":
        if the_type == "Directory":
            if the_format == "PDI_SAFE":
                raise Exception("PDI_SAFE can not be an input of an IDPSC")
            # DECOMP special treatment
            elif task_name == "DECOMP" and the_format == "PDI_GR_LIST":
                the_dir = fully_resolve(context_info["DB"][the_format])
                alternatives.append(the_dir)
                if "PROC.PDI_DS_GR_LIST" in context_info:
                    alternatives.extend(context_info["PROC.PDI_DS_GR_LIST"])
            else:
                the_dir = fully_resolve(context_info["DB"][the_format])
                alternatives.append(the_dir)
                if not os.path.exists(the_dir):
                    mkdir_p(the_dir)
        if the_type == "Physical":
            the_dir = fully_resolve(context_info["DB"][the_format])
            dir_content = os.listdir(the_dir)
            base_dir = the_dir

            if "GIP_R2EQOB" == the_format:
                # pass
                dir_content = filter(lambda x: "GIP_R2EOB2" in x, dir_content)
                alternatives.extend(dir_content)
                if len(dir_content) == 0:
                    raise Exception("No GIPP found for type %s ! (searched for pattern GIP_R2EOB2)" % the_format)
            elif "GIP" in the_format:
                dir_content = filter(lambda x: the_format in x, dir_content)
                """validated = validator(dir_content, the_type)
                log.warning("%s has been validated as format %s with result %s" % (the_dir, the_format, validated) )
                if hasattr(Policies, "get" + an_alternative.Retrieval_Mode):
                    method = getattr(Policies, "get" + an_alternative.Retrieval_Mode)

                if not method:
                    raise Exception("Filtering criteria %s not found !" % an_alternative.Retrieval_Mode)
                
                filtered = method(dir_content, begin, end, tol0, tol1)"""
                alternatives.extend(dir_content)
                if len(dir_content) == 0:
                    raise Exception("No GIPP found for type %s !" % the_format)
            else:
                if len(dir_content) == 0:
                    raise Exception("No files found for type %s !" % the_format)
                alternatives.extend(dir_content)

    if origin == "PROC":
        # keys = [each for each in context_info.keys() if "PROC." in each]
        log.debug("Asking for previous result of %s !!" % the_format)
        # PDI_SAFE exception
        if the_format == "PDI_SAFE":
            raise Exception("PDI_SAFE type can no be an input of an IDPSC")
        # INPUT_OUTPUT_MAPPING
        input_output_mapping = {}
        if "INPUT_OUTPUT_MAPPING" in context_info:
            log.debug("Input_output_mapping found")
            input_output_mapping = context_info["INPUT_OUTPUT_MAPPING"]
        special_treat = False
        extracted_task_name = extract_task_name(task_name)
        if extracted_task_name in input_output_mapping:
            log.debug("In Input_output_mapping for " + task_name)
            if the_format in input_output_mapping[extracted_task_name]:
                special_treat = True
                for f in input_output_mapping[extracted_task_name][the_format]:
                    key = f if f.startswith("PROC.") else ("PROC.LIST." + f)
                    ct_info_list = context_info[key]
                    log.debug("Found context info: %s" % ct_info_list)
                    for task in input_output_mapping[extracted_task_name][the_format][f]:
                        found = False
                        for proc in ct_info_list:
                            if proc[0] == task:
                                alternatives.extend(proc[1])
                                found = True
                        if not found:
                            log.warning(task_name + " " + the_format + " input from " + task + " : " + f + " not found")
                            raise Exception(
                                task_name + " " + the_format + " input from " + task + " : " + f + " not found")
        # Standard method
        if not special_treat:
            if "PROC." + the_format in context_info:
                ct_info = context_info["PROC." + the_format]
                log.debug("Found context info: %s" % ct_info)
                # If is physical (a file)
                if os.path.isfile(ct_info[0]):
                    base_dir = os.path.dirname(ct_info[0])
                    alternatives.append(os.path.basename(ct_info[0]))
                else:
                    alternatives.extend(ct_info)
            else:
                raise Exception("No previous process furnished the file type %s" % the_format)

    log.debug("Working with Input type %s, FFormat %s" % (the_format, the_type))

    return base_dir, alternatives


# Import shell env from JSON
def prepare_shell_environment_for_task(a_task, context_info):
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


# Prepare env for task launch
def prepare_execution_environment_for_task(a_task, context_info):
    log = logging.getLogger("Orchestrator")
    log.info("Preparing execution environments")

    crit_level = a_task.Criticality_Level
    log.info("Critical level %s dully noted" % crit_level)

    task_dir = prepare_base_directory_for_task(a_task, context_info)
    # prepare input dirs
    prepare_inputs(a_task, context_info, task_dir)
    # if input style is copy, copy data
    # else create symlinks
    # prepare output dirs
    prepare_outputs(a_task, context_info, task_dir)

    return task_dir


# Get a directory to work in for a task
def prepare_base_directory_for_task(a_task, context_info):
    log = logging.getLogger("Orchestrator")
    log.info("Prepare base directory")

    task_dir = context_info["BASE_DIR"] + os.sep + a_task.Name
    try:
        os.mkdir(task_dir)
    except OSError:
        if not os.path.exists(task_dir):
            raise

    return task_dir


# prepare the inputs for a task
def prepare_inputs(a_task, context_info, task_dir):
    log = logging.getLogger("Orchestrator")
    log.info("Preparing inputs for task " + a_task.Name)

    if "PREVIOUS.TASK.INPUT" in context_info:
        if context_info["PREVIOUS.TASK.INPUT"][0] == a_task.Name:
            log.debug("Found previous input map")
            return context_info["PREVIOUS.TASK.INPUT"][1]
    working_dir = task_dir + os.sep + "input"
    try:
        os.mkdir(working_dir)
    except OSError as exception:
        if not os.path.exists(working_dir):
            raise

    inputs_map = resolve_inputs(a_task.List_of_Inputs.Input, context_info, working_dir, a_task.Name)

    context_info["PREVIOUS.TASK.INPUT"] = [a_task.Name, inputs_map]

    return inputs_map


# resolve the inputs for a task
def resolve_inputs(inputs_list, context_info, working_dir, task_name):
    log = logging.getLogger("Orchestrator")

    resolved_inputs_map = {}

    log.debug("Input length: %s" % len(inputs_list))
    for subindex in range(len(inputs_list)):
        the_format = inputs_list[subindex].List_of_Alternatives.Alternative.File_Type
        the_type = inputs_list[subindex].List_of_Alternatives.Alternative.File_Name_Type
        the_origin = inputs_list[subindex].List_of_Alternatives.Alternative.Origin

        # WORKING is dynamicaly created
        if the_format == "WORKING":
            continue

        # input type creation
        the_input_type = InputType(the_format, the_type)

        base_dir, alternatives = alternative_processor(inputs_list[subindex].List_of_Alternatives.Alternative,
                                                       context_info, task_name)
        # remove double entry
        alternatives_unique = []
        known_list = set()
        for d in alternatives:
            if d in known_list: continue
            alternatives_unique.append(d)
            known_list.add(d)
        alternatives = alternatives_unique

        resolved_inputs = []
        # Multiple alternatives found for directory
        if len(alternatives) > 1 and not base_dir:
            log.debug("FOLDER FUSION ::: In multiple alternative directory handling")
            the_link_folder = working_dir + os.sep + the_format
            try:
                os.mkdir(the_link_folder)
                log.debug("Folder fusion: Input must be created in %s" % the_link_folder)
            except OSError, e:
                if not os.path.exists(the_link_folder):
                    log.error(e)
                    raise
            for each in alternatives:
                # list the alternative files
                for strRoot, listDirNames, listFileNames in os.walk(each, followlinks=True):
                    # for all dirs underneath
                    for strDirName in listDirNames:
                        str_alternative_dir = os.path.join(strRoot, strDirName)
                        str_link_dir = the_link_folder + os.sep + str_alternative_dir.replace(each, "", 1)
                        if not os.path.exists(str_link_dir):
                            try:
                                os.mkdir(str_link_dir)
                                log.debug("Folder fusion must be created %s" % str_link_dir)
                            except OSError, e:
                                if not os.path.exists(str_link_dir):
                                    log.error(e)
                                    raise
                    # for all files underneath
                    for strFileName in listFileNames:
                        str_alternative_file = os.path.join(strRoot, strFileName)
                        str_link_file = the_link_folder + os.sep + str_alternative_file.replace(each, "", 1)
                        str_rel_alternative_file = os.path.relpath(str_alternative_file, os.path.dirname(str_link_file))
                        if not os.path.exists(str_link_file):
                            log.debug("Folder fusion : We should create a symlink to %s in %s" % (
                                str_alternative_file, str_link_file))
                            try:
                                if the_origin == "DB":
                                    os.symlink(str_alternative_file, str_link_file)
                                else:
                                    os.symlink(str_rel_alternative_file, str_link_file)
                            except OSError, e:
                                log.debug("Folder fusion: Path exist: " + str_link_file)
                                if not os.path.exists(str_link_file):
                                    log.error("Internal error with file: " + str_link_file)
            resolved_inputs.append(the_link_folder)
        else:
            for each in alternatives:
                if base_dir:
                    the_link_name = working_dir + os.sep + each
                    the_link_target = base_dir + os.sep + each
                    the_link_target = the_link_target.replace(context_info["BASE_DIR"], "../..")
                else:
                    the_link_name = working_dir + os.sep + the_format
                    the_link_target = each
                    the_link_target = the_link_target.replace(context_info["BASE_DIR"], "../..")

                if os.path.isabs(the_link_target):
                    if not os.path.exists(the_link_target):
                        raise Exception(
                            "Path to an input folder/file is not valid: " + the_format + " " + the_link_target)
                else:
                    if not os.path.exists(working_dir + os.sep + the_link_target):
                        raise Exception(
                            "Path to an input folder/file is not valid: " + the_format + " " + working_dir + os.sep + the_link_target)
                if not os.path.exists(the_link_name):
                    log.debug("We should create a symlink to %s in %s" % (the_link_target, the_link_name))
                    try:
                        os.symlink(the_link_target, the_link_name)
                    except OSError, e:
                        log.warning("Path exist: " + the_link_name)
                        if not os.path.exists(the_link_name):
                            log.error("Internal error with file: " + the_link_name)
                if task_name.startswith("TP_FILTER-REG") and the_format == "HOMOLOG_POINTS_LIST":
                    resolved_inputs.append(the_link_name + os.sep + "TIE_POINTS")
                elif task_name.startswith("TP_FILTER") and the_format == "HOMOLOG_POINTS_LIST":
                    resolved_inputs.append(the_link_name + os.sep + "GCP_POINTS")
                else:
                    resolved_inputs.append(the_link_name)

        # resolved_inputs = list(set(resolved_inputs))

        name_list = List_of_File_NamesType()
        for file_name in resolved_inputs:
            name_list.add_File_Name(file_name)
        name_list.count = len(resolved_inputs)
        the_input_type.set_List_of_File_Names(name_list)

        resolved_inputs_map[the_format] = (the_input_type, resolved_inputs)

    return resolved_inputs_map


# prepare the outputs for a task
def prepare_outputs(a_task, context_info, task_dir):
    log = logging.getLogger("Orchestrator")
    log.info("Preparing outputs for task " + a_task.Name)
    if "PREVIOUS.TASK.OUTPUT" in context_info:
        if context_info["PREVIOUS.TASK.OUTPUT"][0] == a_task.Name:
            log.debug("Found previous output map")
            return context_info["PREVIOUS.TASK.OUTPUT"][1]

    working_dir = task_dir + os.sep + "output"
    try:
        os.mkdir(working_dir)
    except OSError, e:
        if not os.path.exists(working_dir):
            log.error(e)
            raise

    outputs_map = resolve_outputs(a_task.List_of_Outputs.Output, context_info, working_dir, a_task.Name)

    context_info["PREVIOUS.TASK.OUTPUT"] = [a_task.Name, outputs_map]

    return outputs_map


# resolve the outputs for a task
def resolve_outputs(outputs_list, context_info, working_dir, task_name):
    log = logging.getLogger("Orchestrator")

    resolved_outputs_map = {}

    extracted_task_name = extract_task_name(task_name)
    for subindex in range(len(outputs_list)):
        resolved_outputs = []

        log.debug("[Output] File Name: [%s], Mandatory : [%s], Type : [%s], Destination: [%s]" % (
            outputs_list[subindex].File_Name_Type, outputs_list[subindex].Mandatory, outputs_list[subindex].Type,
            outputs_list[subindex].Destination))
        the_format = outputs_list[subindex].Type
        the_output_type = OutputType(outputs_list[subindex].Mandatory, outputs_list[subindex].Type,
                                     outputs_list[subindex].File_Name_Type, None)

        # todo output generation, None must b replaced
        if outputs_list[subindex].Destination == "DB":
            if outputs_list[subindex].File_Name_Type == "Directory":
                db_dir = fully_resolve(context_info["DB"][the_format])
                if task_name.startswith("TP_FILTER-REG") and the_format == "HOMOLOG_POINTS_LIST":
                    db_dir = db_dir + os.sep + "TIE_POINTS"
                elif task_name.startswith("TP_FILTER") and the_format == "HOMOLOG_POINTS_LIST":
                    db_dir = db_dir + os.sep + "GCP_POINTS"
                resolved_outputs.append(db_dir)
                resolved_outputs_map[the_format] = (the_output_type, resolved_outputs)
            elif outputs_list[subindex].File_Name_Type == "Physical":
                res_output_dir = fully_resolve(context_info["DB"][the_format])
                resolved_outputs.append(res_output_dir + os.sep + the_format.lower() + ".xml")
                resolved_outputs_map[the_format] = (the_output_type, resolved_outputs)
            else:
                raise Exception("Unexpected output criteria...")
        else:
            if outputs_list[subindex].File_Name_Type == "Directory":
                resolved_outputs.append(working_dir + os.sep + the_format)
                try:
                    os.mkdir(resolved_outputs[0])
                    log.debug("[Output] Output must be created in %s" % resolved_outputs[0])
                except OSError, e:
                    if not os.path.exists(resolved_outputs[0]):
                        log.error(e)
                        raise
                resolved_outputs_map[the_format] = (the_output_type, resolved_outputs)
                if "L1A" in task_name:
                    context_info["PROC.L1A.LIST." + the_format] = context_info.setdefault("PROC.L1A.LIST." + the_format,
                                                                                          []) + [
                                                                      [extracted_task_name, resolved_outputs]]
                    context_info["PROC.L1A." + the_format] = resolved_outputs
                    log.debug("Adding L1A %s to PROC" % str(resolved_outputs))
                elif "L1B" in task_name:
                    context_info["PROC.L1B.LIST." + the_format] = context_info.setdefault("PROC.L1B.LIST." + the_format,
                                                                                          []) + [
                                                                      [extracted_task_name, resolved_outputs]]
                    context_info["PROC.L1B." + the_format] = resolved_outputs
                    log.debug("Adding L1B %s to PROC" % str(resolved_outputs))
                elif "L1C" in task_name:
                    context_info["PROC.L1C.LIST." + the_format] = context_info.setdefault("PROC.L1C.LIST." + the_format,
                                                                                          []) + [
                                                                      [extracted_task_name, resolved_outputs]]
                    context_info["PROC.L1C." + the_format] = resolved_outputs
                    log.debug("Adding L1C %s to PROC" % str(resolved_outputs))
                elif "PVI" in task_name:
                    context_info["PROC.PVI.LIST." + the_format] = context_info.setdefault("PROC.PVI.LIST." + the_format,
                                                                                          []) + [
                                                                      [extracted_task_name, resolved_outputs]]
                    context_info["PROC.PVI." + the_format] = resolved_outputs
                    log.debug("Adding PVI %s to PROC" % str(resolved_outputs))
                else:
                    context_info["PROC.LIST." + the_format] = context_info.setdefault("PROC.LIST." + the_format, []) + [
                        [extracted_task_name, resolved_outputs]]
                    context_info["PROC." + the_format] = resolved_outputs
                    log.debug("Adding %s to PROC" % str(resolved_outputs))

            elif outputs_list[subindex].File_Name_Type == "Physical":
                res_output_dir = working_dir + os.sep + the_format
                try:
                    os.mkdir(res_output_dir)
                    log.debug("[Output] Output must be created in %s" % (res_output_dir))
                except OSError, e:
                    if not os.path.exists(res_output_dir):
                        log.error(e)
                        raise
                if the_format == "TILE_LIST_FILE":
                    resolved_outputs.append(res_output_dir + os.sep + "tile_list_file.xml")
                elif the_format == "FRAME_FILE":
                    resolved_outputs.append(res_output_dir + os.sep + "frame_file.xml")
                elif the_format == "REPORT":
                    # REPORT output is dynamicaly generated
                    continue
                else:
                    resolved_outputs.append(res_output_dir + os.sep + the_format.lower() + ".xml")
                resolved_outputs_map[the_format] = (the_output_type, resolved_outputs)
                if "L1A" in task_name:
                    log.debug("Adding L1A %s to PROC" % str(resolved_outputs))
                    context_info["PROC.L1A." + the_format] = resolved_outputs
                elif "L1B" in task_name:
                    log.debug("Adding L1B %s to PROC" % str(resolved_outputs))
                    context_info["PROC.L1B." + the_format] = resolved_outputs
                elif "L1C" in task_name:
                    log.debug("Adding L1C %s to PROC" % str(resolved_outputs))
                    context_info["PROC.L1C." + the_format] = resolved_outputs
                else:
                    log.debug("Adding %s to PROC" % str(resolved_outputs))
                    context_info["PROC." + the_format] = resolved_outputs
            else:
                raise Exception("Unexpected output criteria...")

        the_output_type.set_File_Name(resolved_outputs[0])

    return resolved_outputs_map

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
from TaskTableReader import TaskType, OptionType, List_of_OptionsType
from Scheduler_Task import get_running_parameters
from FileUtils import extract_task_name


def create_tasklist(the_task_table, the_list_of_tasks, context_info):
    task_list = []
    for a_Task in the_list_of_tasks:
        parameters = get_running_parameters(the_task_table, a_Task, context_info)
        if is_a_parallelizable_task(a_Task, parameters):
            sub_tasks = split_into_subtasks(a_Task, context_info, parameters)
            task_list.extend(sub_tasks)
        elif a_Task.Name.startswith("OLQC_GR") or a_Task.Name.startswith("OLQC_TILE"):
            sub_tasks = split_into_olqc(a_Task, context_info, parameters)
            task_list.extend(sub_tasks)
        else:
            task_list.append(a_Task)
    return task_list


def is_a_parallelizable_task(a_task, parameters):
    log = logging.getLogger("Orchestrator")
    # todo check if a_Task if paralelizable looking at its global parameters...
    parallel_candidates = [each for each in parameters.keys() if "PARALLEL" in each]
    if parallel_candidates:
        log.warning("It seems that we can parallelize %s Task" % a_task.Name)
        return True

    return False


# TODO : add a parallelization in config
def split_into_subtasks(a_task, context_info, parameters):
    log = logging.getLogger("Orchestrator")
    # task_list is ready to pass again
    task_list_out = split_into_datablock(a_task, context_info, parameters)
    # get the configured parallelization
    if "Parallelization" in context_info["Config"]:
        for p in context_info["Config"]["Parallelization"]:
            if p[0] == "BAND_QL":
                task_list_out = split_band_ql(task_list_out, p, parameters)
            if p[0] == "BAND":
                task_list_out = split_band(task_list_out, p, parameters)
            if p[0] == "DETECTOR":
                task_list_out = split_detector(task_list_out, p, parameters, a_task.Name)
            if p[0] == "ATF":
                task_list_out = split_atf(task_list_out, p, parameters, context_info, a_task.Name)
            if p[0] == "GRANULE":
                task_list_out = split_granule(task_list_out, p, parameters, context_info, a_task.Name)
            if p[0] == "TILE":
                task_list_out = split_tile(task_list_out, p, parameters, context_info)
    log.info("Task " + a_task.Name + " has been splitted in " + str(len(task_list_out)))
    return task_list_out


def split_band_ql(a_task_list, parallel_info, parameters):
    task_list_out = []
    log = logging.getLogger("Orchestrator")
    if "PARALLEL_BAND_QL" in parameters and "PARALLEL_BAND_QL_IDENT" in parameters:
        if parameters["PARALLEL_BAND_QL"] == "true":
            log.info("Parallelization detected on PARALLEL_BAND_QL_IDENT")
            task_list_out = split_into_subtasklist(a_task_list, "PARALLEL_BAND_QL_IDENT",
                                                   parameters["PARALLEL_BAND_QL_IDENT"], parallel_info[1])
        else:
            task_list_out = a_task_list
    else:
        task_list_out = a_task_list
    return task_list_out


def split_band(a_task_list, parallel_info, parameters):
    task_list_out = []
    log = logging.getLogger("Orchestrator")
    if "PARALLEL_BAND" in parameters and "PARALLEL_BAND_IDENT" in parameters:
        if parameters["PARALLEL_BAND"] == "true":
            log.info("Parallelization detected on PARALLEL_BAND_IDENT")
            task_list_out = split_into_subtasklist(a_task_list, "PARALLEL_BAND_IDENT",
                                                   parameters["PARALLEL_BAND_IDENT"], parallel_info[1])
        else:
            task_list_out = a_task_list
    else:
        task_list_out = a_task_list
    return task_list_out


def split_detector(a_task_list, parallel_info, parameters, a_task_name):
    task_list_out = []
    log = logging.getLogger("Orchestrator")
    no_detector_list = ["FORMAT_IMG_L1A", "FORMAT_IMG_L1B", "UNFORMAT_GRI"]
    nb_split = parallel_info[1]
    if extract_task_name(a_task_name) in no_detector_list:
        nb_split = 12
    if "PARALLEL_DETECTOR" in parameters:
        if parameters["PARALLEL_DETECTOR"] == "true" and "PARALLEL_DETECTOR_IDENT" in parameters:
            log.info("Parallelization detected on PARALLEL_DETECTOR_IDENT")
            task_list_out = split_into_subtasklist(a_task_list, "PARALLEL_DETECTOR_IDENT",
                                                   parameters["PARALLEL_DETECTOR_IDENT"], nb_split)
        else:
            task_list_out = a_task_list
    elif "PARALLEL_DETECTOR_IDENT" in parameters:
        log.info("Parallelization detected on PARALLEL_DETECTOR_IDENT")
        task_list_out = split_into_subtasklist(a_task_list, "PARALLEL_DETECTOR_IDENT",
                                               parameters["PARALLEL_DETECTOR_IDENT"], nb_split)
    else:
        task_list_out = a_task_list
    return task_list_out


def split_atf(a_task_list, parallel_info, parameters, context_info, a_task_name):
    task_list_out = a_task_list
    log = logging.getLogger("Orchestrator")
    no_detector_list = ["RADIO_AB"]
    # The IDPSC is also parallelised by datablocks ?
    datablock_size = get_datablock_size(parameters, context_info)
    if datablock_size == 0:
        log.warning("No datablock size information found")
        return task_list_out

    if "PARALLEL_ATF" in parameters:
        if parameters["PARALLEL_ATF"] == "true":
            if "PARALLEL_ATF_BEGIN_GRANULE" in parameters and "PARALLEL_ATF_END_GRANULE" in parameters:
                log.info("Parallelization detected on PARALLEL_ATF_BEGIN_GRANULE and PARALLEL_ATF_END_GRANULE")
                if len(parallel_info) == 5:
                    log.info("Multisplit requested : " + str(parallel_info[3]) + "/" + str(parallel_info[4]))
                    task_list_out = split_into_subtaskrange_multisplit(a_task_list, "PARALLEL_ATF_BEGIN_GRANULE",
                                                                       "PARALLEL_ATF_END_GRANULE", datablock_size,
                                                                       parallel_info[1],
                                                                       parallel_info[3], parallel_info[4])
                else:
                    task_list_out = split_into_subtaskrange(a_task_list, "PARALLEL_ATF_BEGIN_GRANULE",
                                                            "PARALLEL_ATF_END_GRANULE", datablock_size,
                                                            parallel_info[1])
            if "PARALLEL_ATF_DETECTOR_IDENT" in parameters:
                log.info("Parallelization detected on PARALLEL_ATF_DETECTOR_IDENT")
                if extract_task_name(a_task_name) in no_detector_list:
                    task_list_out = split_into_subtasklist(task_list_out, "PARALLEL_ATF_DETECTOR_IDENT",
                                                           parameters["PARALLEL_ATF_DETECTOR_IDENT"], 12)
                else:
                    task_list_out = split_into_subtasklist(task_list_out, "PARALLEL_ATF_DETECTOR_IDENT",
                                                           parameters["PARALLEL_ATF_DETECTOR_IDENT"], parallel_info[2])
            if "PARALLEL_V_ATF_NUMBER" in parameters:
                log.info("Parallelization detected on PARALLEL_V_ATF_NUMBER")
                num_atf = context_info["SEG_SIZE"]
                parallel_atf_number = "0001"
                for i in range(1, num_atf):
                    parallel_atf_number += '-%04d' % (i + 1)
                task_list_out = split_into_subtasklist(a_task_list, "PARALLEL_V_ATF_NUMBER", parallel_atf_number,
                                                       num_atf)

    # FORMAT_ISP ATF exception
    if "PARALLEL_ATF" in parameters and not "PARALLEL_GRANULE" in parameters and "PARALLEL_GRANULE_BEGIN" in parameters and "PARALLEL_GRANULE_END" in parameters:
        if parameters["PARALLEL_ATF"] == "true":
            log.info("FORMAT_ISP special parallelization detected on PARALLEL_GRANULE_BEGIN and PARALLEL_GRANULE_END")
            if len(parallel_info) == 5:
                log.info("Multisplit requested : " + str(parallel_info[3]) + "/" + str(parallel_info[4]))
                task_list_out = split_into_subtaskrange_multisplit(
                    a_task_list, "PARALLEL_GRANULE_BEGIN", "PARALLEL_GRANULE_END",
                    datablock_size, parallel_info[1], parallel_info[3], parallel_info[4])
            else:
                task_list_out = split_into_subtaskrange(a_task_list, "PARALLEL_GRANULE_BEGIN", "PARALLEL_GRANULE_END",
                                                        datablock_size, parallel_info[1])

    return task_list_out


def split_granule(a_task_list, parallel_info, parameters, context_info, a_task_name):
    log = logging.getLogger("Orchestrator")
    task_list_out = a_task_list
    no_detector_list = []
    # The IDPSC is also parallelised by datablocks ?
    datablock_size = get_datablock_size(parameters, context_info)
    if datablock_size == 0:
        log.warning("No datablock size information found")
        return task_list_out

    if "PARALLEL_GRANULE" in parameters:
        if "PARALLEL_GRANULE_BEGIN" in parameters and "PARALLEL_GRANULE_END" in parameters \
                and parameters["PARALLEL_GRANULE"] == "true":
            log.info("Parallelization detected on PARALLEL_GRANULE_BEGIN and PARALLEL_GRANULE_END")
            task_list_out = split_into_subtaskrange(a_task_list, "PARALLEL_GRANULE_BEGIN", "PARALLEL_GRANULE_END",
                                                    datablock_size, parallel_info[1])

    if extract_task_name(a_task_name) == "UNFORMAT_GRI":
        gri_size = context_info["GRI_SIZE"]
        if "PARALLEL_GRANULE_BEGIN" in parameters and "PARALLEL_GRANULE_END" in parameters \
                and "MASK_AGGREGATION" in parameters and "GRI_DECOMPRESSION":
            if parameters["GRI_DECOMPRESSION"] == "true":
                log.info("Parallelization detected on PARALLEL_GRANULE_BEGIN and PARALLEL_GRANULE_END for UNFORMAT_GRI")
                task_list_out = split_into_subtaskrange(a_task_list, "PARALLEL_GRANULE_BEGIN", "PARALLEL_GRANULE_END",
                                                        gri_size, parallel_info[1])
    return task_list_out


def split_tile(a_task_list, parallel_info, parameters, context_info):
    log = logging.getLogger("Orchestrator")
    task_list_out = a_task_list
    # The IDPSC is also parallelised by datablocks ?
    datablock_size = get_datablock_size(parameters, context_info)
    if datablock_size == 0:
        log.warning("No datablock size information found")
        return task_list_out

    if "PARALLEL_TILE" in parameters:
        if parameters["PARALLEL_TILE"] == "true":
            if "PARALLEL_TILE_IDENT" in parameters:
                log.info("Parallelization detected on PARALLEL_TILE_IDENT")
                parallel_tile_ident = "001"
                for i in range(1, datablock_size):
                    parallel_tile_ident += '-%03d' % (i + 1)
                task_list_out = split_into_subtasklist(a_task_list, "PARALLEL_TILE_IDENT", parallel_tile_ident,
                                                       parallel_info[1])
    return task_list_out


def split_into_olqc(a_task, context_info, parameters):
    log = logging.getLogger("Orchestrator")
    task_list_out = []
    # get the configured parallelization
    if "OLQC_Instances" in context_info["Config"]:
        nb_instance = int(context_info["Config"]["OLQC_Instances"])
        for i in range(nb_instance):
            task_list_out.append(copy_task(a_task))
    else:
        task_list_out.append(a_task)
    log.info("Task " + a_task.Name + " has been splitted in " + str(len(task_list_out)))
    return task_list_out


# Treat datablock
def split_into_datablock(a_task, context_info, parameters):
    task_list_out = []
    log = logging.getLogger("Orchestrator")
    # PARALLEL DATABLOCK is explicitly to false: don't cut
    if "PARALLEL_DATABLOCK" in parameters:
        if parameters["PARALLEL_DATABLOCK"] == "false":
            task_list_out.append(a_task)
            return task_list_out

    datablocks = context_info["DATABLOCK_SIZE"]
    if "DATABLOCK_NUMBER" in parameters and len(datablocks) != 0:
        for d in datablocks:
            new_option = OptionType("DATABLOCK_NUMBER", "String", d)
            tmp_task = copy_task_replace_option(a_task, new_option)
            task_list_out.append(tmp_task)
    else:
        task_list_out.append(a_task)

    return task_list_out


# get the datablock size
def get_datablock_size(parameters, context_info):
    datablock_size = 0
    if "DATABLOCK_NUMBER" in parameters:
        datablock_str = parameters["DATABLOCK_NUMBER"]
        if datablock_str in context_info["DATABLOCK_SIZE"]:
            datablock_size = int(context_info["DATABLOCK_SIZE"][datablock_str])
    elif "DATABLOCK_SIZE" in context_info:
        for d in context_info["DATABLOCK_SIZE"]:
            datablock_size += int(context_info["DATABLOCK_SIZE"][d])
    return datablock_size


# Treat lists
def split_into_subtasklist(a_task_list, parameter_name, parameter_value, nb_split):
    task_list_out = []
    log = logging.getLogger("Orchestrator")
    # PARALLEL XXXXXXX is explicitly to false: don't cut
    elements = split_list(parameter_value, nb_split)
    for d in elements:
        for task in a_task_list:
            new_option = OptionType(parameter_name, "String", d)
            tmp_task = copy_task_replace_option(task, new_option)
            task_list_out.append(tmp_task)
    return task_list_out


# cut a list with "-" in n sublist
def split_list(alist, nb_split):
    out_list = []
    if nb_split == 1:
        return [alist]
    tmp_list = alist.split("-")
    real_split = nb_split
    if len(tmp_list) <= nb_split:
        real_split = len(tmp_list)
    nb_persplit = int(len(tmp_list) / real_split)
    nb_used = 0
    for s in range(0, real_split):
        nb_persplit = int((len(tmp_list) - nb_used) / (real_split - s))
        tmp_str = tmp_list[nb_used]
        nb_used += 1
        for e in range(1, nb_persplit):
            tmp_str += "-" + tmp_list[nb_used]
            nb_used += 1
        out_list.append(tmp_str)
    return out_list


# Treat lists
def split_into_subtaskrange(a_task_list, parameter_begin_name, parameter_end_name, a_range, nb_split):
    task_list_out = []
    elements = split_range(a_range, nb_split)
    for d in elements:
        for task in a_task_list:
            new_option_begin = OptionType(parameter_begin_name, "String", d[0])
            new_option_end = OptionType(parameter_end_name, "String", d[1])
            tmp_task = copy_task_replace_options(task, new_option_begin, new_option_end)
            task_list_out.append(tmp_task)
    return task_list_out


# cut the range 1-anumber in n_sublist
def split_range(anumber, nb_split):
    out_list = []
    real_split = nb_split
    if nb_split == 1:
        return [["001", '%03d' % anumber]]
    if anumber <= nb_split:
        real_split = anumber
    nb_persplit = int(anumber / real_split)
    nb_used = 0
    for s in range(0, real_split):
        nb_persplit = (anumber - nb_used) / (real_split - s)
        out_list.append(['%03d' % (nb_used + 1), '%03d' % (nb_used + nb_persplit)])
        nb_used += nb_persplit
    return out_list


# Treat lists
def split_into_subtaskrange_multisplit(a_task_list, parameter_begin_name, parameter_end_name, a_range,
                                       nb_split, multisplit_split, multisplit_total):
    task_list_out = []
    elements = split_range_multisplit(a_range, nb_split, multisplit_split, multisplit_total)
    for d in elements:
        for task in a_task_list:
            new_option_begin = OptionType(parameter_begin_name, "String", d[0])
            new_option_end = OptionType(parameter_end_name, "String", d[1])
            tmp_task = copy_task_replace_options(task, new_option_begin, new_option_end)
            task_list_out.append(tmp_task)
    return task_list_out


# cut the range 1-anumber in n_sublist, with multisplit only consider the multisplit_split on multisplit_total
def split_range_multisplit(anumber, nb_split, multisplit_split, multisplit_total):
    multisplit_per_split = anumber / multisplit_total
    multisplit_this_split_start = multisplit_per_split * (multisplit_split - 1)
    multisplit_this_split_stop = min(multisplit_per_split * multisplit_split, anumber)
    multisplit_this_split_nbelements = multisplit_this_split_stop - multisplit_this_split_start
    log = logging.getLogger("Orchestrator")
    log.debug("Requesting multisplit : " + str(multisplit_split) + "/" + str(multisplit_total))
    log.debug("this multisplit : " + str(multisplit_this_split_start) + "/" + str(multisplit_this_split_stop)
              + "/"+ str(anumber))
    out_list = []
    real_split = nb_split
    if nb_split == 1:
        return [['%03d' % multisplit_this_split_start, '%03d' % multisplit_this_split_stop]]
    if multisplit_this_split_nbelements <= nb_split:
        real_split = multisplit_this_split_nbelements
    nb_used = multisplit_this_split_start
    for s in range(0, real_split):
        nb_persplit = (multisplit_this_split_stop - nb_used) / (real_split - s)
        out_list.append(['%03d' % (nb_used + 1), '%03d' % (nb_used + nb_persplit)])
        nb_used += nb_persplit
    return out_list


# Function to copy a task and replace one option
def copy_task_replace_option(a_task, option):
    # First assign non changing elements
    tmp_task = TaskType()
    tmp_task.Name = a_task.Name
    tmp_task.Version = a_task.Version
    tmp_task.Critical = a_task.Critical
    tmp_task.Criticality_Level = a_task.Criticality_Level
    tmp_task.File_Name = a_task.File_Name
    tmp_task.List_of_Inputs = a_task.List_of_Inputs
    tmp_task.List_of_Outputs = a_task.List_of_Outputs
    tmp_task.List_of_Breakpoints = a_task.List_of_Breakpoints
    tmp_task.NumberOfCPUs = a_task.NumberOfCPUs
    # filling option: parallelization parameters to be changed
    tmp_task_option = List_of_OptionsType()
    options_list = a_task.List_of_Options.Option
    # add the parallel parameters
    tmp_task_option.add_Option(option)
    for subindex in range(len(options_list)):
        current_option = options_list[subindex]
        # ignore any previous parameter with the option name
        if not current_option.Name == option.Name:
            tmp_task_option.add_Option(current_option)
    tmp_task.List_of_Options = tmp_task_option
    return tmp_task


# Function to copy a task and replace one option
def copy_task_replace_options(a_task, option1, option2):
    # First assign non changing elements
    tmp_task = TaskType()
    tmp_task.Name = a_task.Name
    tmp_task.Version = a_task.Version
    tmp_task.Critical = a_task.Critical
    tmp_task.Criticality_Level = a_task.Criticality_Level
    tmp_task.File_Name = a_task.File_Name
    tmp_task.List_of_Inputs = a_task.List_of_Inputs
    tmp_task.List_of_Outputs = a_task.List_of_Outputs
    tmp_task.List_of_Breakpoints = a_task.List_of_Breakpoints
    tmp_task.NumberOfCPUs = a_task.NumberOfCPUs
    # filling option: parallelization parameters to be changed
    tmp_task_option = List_of_OptionsType()
    options_list = a_task.List_of_Options.Option
    # add the parallel parameters
    tmp_task_option.add_Option(option1)
    tmp_task_option.add_Option(option2)
    for subindex in range(len(options_list)):
        current_option = options_list[subindex]
        # ignore any previous parameter with the option name
        if not current_option.Name == option1.Name and not current_option.Name == option2.Name:
            tmp_task_option.add_Option(current_option)
    tmp_task.List_of_Options = tmp_task_option

    return tmp_task


# Function to copy a task
def copy_task(a_task):
    # First assign non changing elements
    tmp_task = TaskType()
    tmp_task.Name = a_task.Name
    tmp_task.Version = a_task.Version
    tmp_task.Critical = a_task.Critical
    tmp_task.Criticality_Level = a_task.Criticality_Level
    tmp_task.File_Name = a_task.File_Name
    tmp_task.List_of_Inputs = a_task.List_of_Inputs
    tmp_task.List_of_Outputs = a_task.List_of_Outputs
    tmp_task.List_of_Breakpoints = a_task.List_of_Breakpoints
    tmp_task.NumberOfCPUs = a_task.NumberOfCPUs
    # filling option: parallelization parameters to be changed
    tmp_task_option = List_of_OptionsType()
    options_list = a_task.List_of_Options.Option
    # add the parallel parameters
    for subindex in range(len(options_list)):
        current_option = options_list[subindex]
        tmp_task_option.add_Option(current_option)
    tmp_task.List_of_Options = tmp_task_option
    return tmp_task

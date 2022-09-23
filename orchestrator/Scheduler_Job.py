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
#  Copyright (C) 2014-2022 CS GROUP – France, https://www.csgroup.eu
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
import os
import StringIO

from JobOrderReader import Ipf_ConfType, Ipf_Proc, List_of_Ipf_ProcsType, Ipf_Job_OrderType, \
    List_of_InputsType, List_of_OutputsType
from JobOrderReader import Sensing_TimeType
from JobOrderReader import Config_FilesType
from JobOrderReader import Dynamic_Processing_ParametersType
from JobOrderReader import Processing_Parameter
from JobOrderReader import InputType, List_of_File_NamesType
from JobOrderReader import OutputType
from FileUtils import extract_task_name

INDENT_JOB = ""


# xml dump in string
def joborder_dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Job_Order',
        namespacedef_='',
        pretty_print=True)
    return output


# Create a jobOrder
def create_joborder(the_task_table, a_task, context_info, local_params, input_map, output_map, task_dir):
    log = logging.getLogger("Orchestrator")
    log.info(INDENT_JOB + "Creating JobOrder...")
    str_pid = str(os.getpid())

    parameters = []
    icd_parameters = context_info["ICD_parameters"]
    if "COMMON" in icd_parameters.keys():
        common_parameters = icd_parameters["COMMON"]
        for t in range(len(common_parameters)):
            task_param = common_parameters[t]
            parameters.append(Processing_Parameter(task_param[0], local_params[task_param[0]]))
    if extract_task_name(a_task.Name) in icd_parameters.keys():
        task_parameters = icd_parameters[extract_task_name(a_task.Name)]
        for t in range(len(task_parameters)):
            task_param = task_parameters[t]
            parameters.append(Processing_Parameter(task_param[0], local_params[task_param[0]]))

    da_conf = Ipf_ConfType()
    da_config_files = Config_FilesType()
    da_conf.set_Config_Files(da_config_files)
    da_conf.set_Processor_Name("Chain")
    da_conf.set_Version("01.03.00")
    da_conf.set_Test(False)
    da_conf.set_Acquisition_Station("MTI_")
    da_conf.set_Processing_Station("MTI_")
    # Fill elements with the config
    if "Config" in context_info:
        if "Stdout_Log_Level" in context_info["Config"]:
            da_conf.set_Stdout_Log_Level(context_info["Config"]["Stdout_Log_Level"])
        if "Stderr_Log_Level" in context_info["Config"]:
            da_conf.set_Stderr_Log_Level(context_info["Config"]["Stderr_Log_Level"])
        if "Processor_Name" in context_info["Config"]:
            da_conf.set_Processor_Name(context_info["Config"]["Processor_Name"])
        if "Version" in context_info["Config"]:
            da_conf.set_Version(context_info["Config"]["Version"])
        if "Acquisition_Station" in context_info["Config"]:
            da_conf.set_Acquisition_Station(context_info["Config"]["Acquisition_Station"])
        if "Processing_Station" in context_info["Config"]:
            da_conf.set_Processing_Station(context_info["Config"]["Processing_Station"])

    # Sensing time
    if "Sensing" in context_info and the_task_table.get_Sensing_Time_Flag() is True:
        sensing_start = context_info["Sensing"][0]
        sensing_stop = context_info["Sensing"][1]
        da_conf.set_Sensing_Time(Sensing_TimeType(sensing_start, sensing_stop))

    da_conf.set_Dynamic_Processing_Parameters(Dynamic_Processing_ParametersType(parameters))

    inputs = a_task.List_of_Inputs
    if len(inputs.Input) != int(inputs.count):
        log.debug(INDENT_JOB + "Inconsistent input length: %s" % str(len(inputs.Input)))

    recovered_inputs_list = [each[0] for each in list(input_map.values())]

    outputs = a_task.List_of_Outputs
    if len(outputs.Output) != int(outputs.count):
        log.debug(INDENT_JOB + "Inconsistent outputs length")

    recovered_outputs_list = [each[0] for each in list(output_map.values())]

    # Build inputs
    working_found = False
    idp_infos_found = False
    da_inputs = List_of_InputsType()
    for a_input in recovered_inputs_list:
        if a_input.File_Type == "IDP_INFOS":
            idp_infos_found = True
        da_inputs.add_Input(a_input)
    da_inputs.count = len(recovered_inputs_list) + 1

    # add WORKING, Directory
    nt = List_of_File_NamesType()
    nt.add_File_Name(task_dir + os.sep + "tmp_" + str_pid)
    nt.set_count(1)
    if not os.path.exists(task_dir + os.sep + "tmp_" + str_pid):
        log.debug(INDENT_JOB + "[Output] WORKING_DIR must be created in %s" % task_dir + os.sep + "tmp_" + str_pid)
        os.mkdir(task_dir + os.sep + "tmp_" + str_pid)
    working_input = InputType("WORKING", "Directory", nt)
    da_inputs.add_Input(working_input)

    # add IDP_INFOS
    if not idp_infos_found:
        base_dir = context_info["BASE_DIR"]
        nt = List_of_File_NamesType()
        nt.add_File_Name(base_dir + os.sep + "IDP_INFOS" + os.sep + "idp_infos.xml")
        nt.set_count(1)
        if os.path.exists(base_dir + os.sep + "IDP_INFOS" + os.sep + "idp_infos.xml"):
            working_input = InputType("IDP_INFOS", "Physical", nt)
            da_inputs.add_Input(working_input)
        else:
            raise Exception("IDP_INFOS file not found")

    # Build outputs
    da_outputs = List_of_OutputsType()
    for a_output in recovered_outputs_list:
        da_outputs.add_Output(a_output)
        if the_task_table.get_Test() == "true":
            if a_output.File_Name_Type == 'Physical':
                open(a_output.get_File_Name(), 'w')
            elif a_output.File_Name_Type == 'Directory':
                open(
                    a_output.get_File_Name() + os.sep + a_task.Name + "_" + a_output.File_Type + "_" + str_pid + ".xml",
                    'w')
    da_outputs.count = len(recovered_outputs_list) + 1

    # add REPORT
    working_output = OutputType(True, "REPORT", "Physical",
                                task_dir + os.sep + "REPORT_" + str_pid + os.sep + "report.xml")
    if not os.path.exists(task_dir + os.sep + "REPORT_" + str_pid):
        log.debug(INDENT_JOB + "[Output] REPORT must be created in %s" % task_dir + os.sep + "REPORT_" + str_pid)
        os.mkdir(task_dir + os.sep + "REPORT_" + str_pid)
    if working_output.File_Name_Type == 'Physical' and the_task_table.get_Test() == "true":
        open(working_output.get_File_Name(), 'w')
    da_outputs.add_Output(working_output)

    procs = List_of_Ipf_ProcsType()
    proc = Ipf_Proc()
    proc.set_Task_Name(extract_task_name(a_task.Name))
    if a_task.Name.startswith("OLQC"):
        proc.set_Task_Name("OLQC")
    proc.set_Task_Version(a_task.Version)
    proc.set_List_of_Inputs(da_inputs)
    proc.set_List_of_Outputs(da_outputs)
    procs.add_Ipf_Proc(proc)
    procs.count = 1

    joborder = Ipf_Job_OrderType(da_conf, procs)

    content = joborder_dom_to_string(joborder).getvalue()
    content = content.replace("    ", "  ")
    # content = content.replace('  xmlns:ipf_base="http://gs2.esa.int/DICO/1.0/IPF/base/" ', '')

    return content

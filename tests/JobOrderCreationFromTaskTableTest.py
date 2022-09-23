import StringIO
import unittest

import xmltodict

from orchestrator.JobOrderReader import Dynamic_Processing_ParametersType
from orchestrator.JobOrderReader import InputType
from orchestrator.JobOrderReader import Ipf_ConfType
from orchestrator.JobOrderReader import Ipf_Job_OrderType
from orchestrator.JobOrderReader import Ipf_Proc
from orchestrator.JobOrderReader import List_of_InputsType
from orchestrator.JobOrderReader import List_of_Ipf_ProcsType
from orchestrator.JobOrderReader import List_of_OutputsType
from orchestrator.JobOrderReader import OutputType
from orchestrator.JobOrderReader import Processing_Parameter
from orchestrator.JobOrderReader import Sensing_TimeType
from orchestrator.TaskTableReader import Dyn_ProcParamType
from orchestrator.TaskTableReader import parse


def dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Task_Table',
        namespacedef_='',
        pretty_print=True)
    return output


def joborder_dom_to_string(dom_object):
    output = StringIO.StringIO()
    output.write('<?xml version="1.0" ?>\n')
    dom_object.export(
        output, 0, name_='Ipf_Job_Order',
        namespacedef_='',
        pretty_print=True)
    return output


def resolve_inputs(param):
    pass


def resolve_outputs(params):
    pass


class JobOrderCreationFromTaskTable(unittest.TestCase):
    def runTest(self):
        TaskTableObjectModel = parse("TaskTable_L0c.xml", silence=True)
        dict_document_2 = xmltodict.parse(dom_to_string(TaskTableObjectModel).getvalue())

        pool0 = TaskTableObjectModel.List_of_Pools.Pool[0]
        inputs = pool0.List_of_Tasks.Task[0].List_of_Inputs

        the_inputs = []
        for subindex in range(int(inputs.count)):
            the_inputs.append(InputType(inputs.Input[subindex].List_of_Alternatives.Alternative.File_Type,
                                        inputs.Input[subindex].List_of_Alternatives.Alternative.File_Name_Type))

        outputs = pool0.List_of_Tasks.Task[0].List_of_Outputs
        if len(outputs.Output) != int(outputs.count):
            print("Inconsistent outputs length")

        the_job_outputs = []
        for subindex in range(len(outputs.Output)):
            the_job_outputs.append(OutputType(outputs.Output[subindex].Mandatory, outputs.Output[subindex].Type,
                                              outputs.Output[subindex].File_Name_Type, None))
            print outputs.Output[subindex].Type
            print outputs.Output[subindex].Destination

        propa = Dyn_ProcParamType()
        propa.get_Param_Name()
        disappear = []
        pp = TaskTableObjectModel.get_List_of_Dyn_ProcParam().get_Dyn_ProcParam()
        for each in pp:
            disappear.append(Processing_Parameter(each.get_Param_Name()[0], each.get_Param_Default()))

        number_of_pools = int(dict_document_2["Ipf_Task_Table"]["List_of_Pools"]["@count"])
        assert number_of_pools == 5
        assert int(TaskTableObjectModel.List_of_Pools.count) == 5

        da_conf = Ipf_ConfType()
        da_conf.set_Processor_Name("INIT_LOC_L0")
        da_conf.set_Version(1.03)
        da_conf.set_Test(False)
        da_conf.set_Acquisition_Station("CGS1")
        da_conf.set_Processing_Station("CGS1")
        da_conf.set_Sensing_Time(Sensing_TimeType("1983-01-01T00:00:00", "2020-01-01T00:00:00"))

        da_conf.set_Dynamic_Processing_Parameters(Dynamic_Processing_ParametersType(disappear))

        # Build inputs

        da_inputs = List_of_InputsType()
        for a_input in the_inputs:
            da_inputs.add_Input(a_input)

        # Build outputs

        da_outputs = List_of_OutputsType()
        for a_output in the_job_outputs:
            da_outputs.add_Output(a_output)

        procs = List_of_Ipf_ProcsType()
        proc = Ipf_Proc()
        proc.set_Task_Name("INIT_LOC_L0")
        proc.set_Task_Version(1.03)
        proc.set_List_of_Inputs(da_inputs)
        proc.set_List_of_Outputs(da_outputs)

        joborder = Ipf_Job_OrderType(da_conf, proc)

        print joborder_dom_to_string(joborder).getvalue()


if __name__ == '__main__':
    unittest.main()

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
import re

from orchestrator.FileUtils import parse_filename


# <Instance_Id> = <Site Centre>_<Creation Date>_<Sensing Time>_<Detector ID>_<Processing Baseline>
def is_granule_pdi(file_name):
    result = parse_filename(file_name)
    instance_id = result[4][1]
    p = re.compile(
        "(CGS1|CGS2|CGS3|CGS4|PAC1|MPCC)_([0-9]{8}T[0-9]{6})_S([0-9]{8}T[0-9]{6})_D([0-9]{2})_N([0-9]{2}\.[0-9]{2}).*(\.[A-Z|a-z]{3})?")
    return p.match(instance_id)


# <Instance_Id> = <Site Centre>_<Creation Date>_<Sensing Time>_<Detector ID>_<Band ID>_<Product_Type>
# S2A_OPER_MSK_TECQUA_CGS1_20141104T134012_S20141104T134012_D03_B03_MSIL1A.gml
def is_granule_pdi_l1a(file_name):
    result = parse_filename(file_name)
    instance_id = result[4][1]
    p = re.compile(
        "(CGS1|CGS2|CGS3|CGS4|PAC1|MPCC)_([0-9]{8}T[0-9]{6})_S([0-9]{8}T[0-9]{6})_D([0-9]{2})_B([A-B|0-9]{2}).*(\.[A-Z|a-z]{3})?")
    return p.match(instance_id)


def is_l1a_mask(file_name):
    result = parse_filename(file_name)
    file_type = result[2][1] + result[3][1]
    p = re.compile("MSK_CLOLOW|MSK_TECQUA|MSK_DEFECT|MSK_SATURA|MSK_NODATA")
    assert p.match(file_type) is not None
    instance_id = result[4][1]
    p = re.compile(
        "(CGS1|CGS2|CGS3|CGS4|PAC1|MPCC)_([0-9]{8}T[0-9]{6})_S([0-9]{8}T[0-9]{6})_D([0-9]{2})_B([A-B|0-9]{2})_(MSIL1A).*(\.[A-Z|a-z]{3})?")
    return p.match(instance_id)


def is_l1b_mask(file_name):
    result = parse_filename(file_name)
    file_type = result[2][1] + result[3][1]
    p = re.compile("MSK_CLOUDS|MSK_TECQUA|MSK_LANWAT|MSK_DETFOO|MSK_DEFECT|MSK_SATURA|MSK_NODATA")
    assert p.match(file_type) is not None
    instance_id = result[4][1]
    p = re.compile(
        "(CGS1|CGS2|CGS3|CGS4|PAC1|MPCC)_([0-9]{8}T[0-9]{6})_S([0-9]{8}T[0-9]{6})_D([0-9]{2})_B([A-B|0-9]{2})_(MSIL1B).*(\.[A-Z|a-z]{3})?")
    return p.match(instance_id)


def is_l1c_mask(file_name):
    result = parse_filename(file_name)
    file_type = result[2][1] + result[3][1]
    p = re.compile("MSK_CLOUDS|MSK_TECQUA|MSK_LANWAT|MSK_DETFOO|MSK_DEFECT|MSK_SATURA|MSK_NODATA")
    assert p.match(file_type) is not None
    instance_id = result[4][1]
    p = re.compile(
        "(CGS1|CGS2|CGS3|CGS4|PAC1|MPCC)_([0-9]{8}T[0-9]{6})_A([0-9]{6})_T([A-Z|0-9]{5})_B([A-B|0-9]{2})_(MSIL1C).*(\.[A-Z|a-z]{3})?")
    return p.match(instance_id)

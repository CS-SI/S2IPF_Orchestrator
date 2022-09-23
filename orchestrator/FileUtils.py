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
import os

'''
    Common file utils
'''


# Resolve a path with env var
def fully_resolve(a_path, check_existence=False):
    resolved = os.path.expanduser(os.path.expandvars(a_path))
    if "$" in resolved:
        raise Exception("Environment variable not resolved in %s" % resolved)
    if check_existence:
        if not os.path.exists(resolved):
            raise Exception("File not found %s" % resolved)
    return resolved


# merge the input folder in the given one by puting symbolic links to files
def folder_fusion(an_input_dir, a_dest_dir):
    try:
        os.mkdir(a_dest_dir)
    except OSError, e:
        if not os.path.exists(a_dest_dir):
            raise
    # list the alternative files
    for strRoot, listDirNames, listFileNames in os.walk(an_input_dir):
        # for all dirs underneath
        for strDirName in listDirNames:
            str_alternative_dir = os.path.join(strRoot, strDirName)
            str_link_dir = a_dest_dir + os.sep + str_alternative_dir.replace(an_input_dir, "", 1)
            if not os.path.exists(str_link_dir):
                try:
                    os.mkdir(str_link_dir)
                except OSError, e:
                    if not os.path.exists(str_link_dir):
                        raise
        # for all files underneath
        for strFileName in listFileNames:
            str_alternative_file = os.path.join(strRoot, strFileName)
            str_link_file = a_dest_dir + os.sep + str_alternative_file.replace(an_input_dir, "", 1)
            str_rel_alternative_file = os.path.relpath(str_alternative_file, os.path.dirname(str_link_file))
            if not os.path.exists(str_link_file):
                try:
                    os.symlink(str_rel_alternative_file, str_link_file)
                except OSError, e:
                    if not os.path.exists(str_link_file):
                        raise Exception("Internal error with file: " + str_link_file)


# extract real task_name from TaskTable task name
def extract_task_name(a_task_name):
    return (a_task_name.split("-"))[0]


def is_a_valid_filename(the_file_name):
    p = re.compile('(S2A|S2B|S2_)_([A-Z|0-9]{4})_([A-Z|0-9|_]{4})([A-Z|0-9|_]{6})_([A-Z|0-9|_|\.]+)')
    return p.match(the_file_name)


def parse_filename(the_file_name):
    p = re.compile('(S2A|S2B|S2_)_([A-Z|0-9]{4})_([A-Z|0-9|_]{4})([A-Z|0-9|_]{6})_([A-Z|0-9|_|\.]+)')
    ama = p.match(the_file_name)
    if not ama:
        return ama
    items = ama.groups()
    result = [("Mission_ID", items[0]), ("File_Class", items[1]), ("File_Category", items[2]),
              ("File_Semantic", items[3]), ("Instance_ID", items[4])]
    return result


def parse_all(the_file_name):
    first_part = parse_filename(the_file_name)
    if first_part:
        second_part = get_instance_id(first_part[4][1])
        if second_part:
            fragments = fragment_data(second_part[-1][-1])
            third_part = map(process_fragment, fragments)
            if third_part:
                result = []
                result.extend(list(first_part))
                result.extend(list(second_part))
                result.extend(list(third_part))
                return result
    return None


def parse_all_as_dict(the_file_name):
    parsed = parse_all(the_file_name)
    if not parsed:
        return None
    map_props = {}
    for each in parsed:
        map_props[each[0]] = each[1]
    return map_props


def is_instance_id(the_file_name):
    time_instance = re.compile('([A-Z|0-9|_]{4})_([0-9]{8})T([0-9]{6})(_[S|O|V|D|A|R|T|N|B|W|L][A-Z|0-9|_|\.]+)?')
    return time_instance.match(the_file_name)


def get_instance_id(the_file_name):
    time_instance = re.compile('([A-Z|0-9|_]{4})_([0-9]{8}T[0-9]{6})(_[S|O|V|D|A|R|T|N|B|W|L][A-Z|0-9|_|\.]+)?')
    ama = time_instance.match(the_file_name)
    items = ama.groups()
    result = [("Site_Centre", items[0]), ("Creation_Date", items[1]), ("Optional_Suffix", items[2])]
    return result


def fragment_data(the_file_name_fragment):
    file_name_fragment = re.compile(
        "_S[0-9]{8}T[0-9]{6}|_O[0-9]{6}T[0-9]{6}|_V[0-9]{8}[T]?[0-9]{6}_[0-9]{8}[T]?[0-9]{6}|_D[0-9]{2}|_A[0-9]{6}|_R[0-9]{3}|_T[A-Z|0-9]{5}|_N[0-9]{2}\.[0-9]{2}|_B[A-B|0-9]{2}|_W[F|P]|_L[N|D]")
    return file_name_fragment.findall(the_file_name_fragment)


def applicability_start(fragment):
    p = re.compile("_S([0-9]{8}T[0-9]{6})")
    ama = p.match(fragment)
    return p.match(fragment)


def orbit_period(fragment):
    p = re.compile("_O([0-9]{6}T[0-9]{6})")
    return p.match(fragment)


def applicability_time_period(fragment):
    p = re.compile("_V([0-9]{8}[T]?[0-9]{6}_[0-9]{8}[T]?[0-9]{6})")
    return p.match(fragment)


def detector_id(fragment):
    p = re.compile("_D([0-9]{2})")
    return p.match(fragment)


def absolute_orbit_number(fragment):
    p = re.compile("_A([0-9]{6})")
    return p.match(fragment)


def relative_orbit_number(fragment):
    p = re.compile("_R([0-9]{3})")
    return p.match(fragment)


def tile_number(fragment):
    p = re.compile("_T([A-Z|0-9]{5})")
    return p.match(fragment)


def processing_baseline(fragment):
    p = re.compile("_N([0-9]{2}\.[0-9]{2})")
    return p.match(fragment)


def band_index(fragment):
    p = re.compile("_B([A-B|0-9]{2})")
    return p.match(fragment)


def completeness_id(fragment):
    p = re.compile("_W([F|P])")
    return p.match(fragment)


def degradation(fragment):
    p = re.compile("_L([N|D])")
    return p.match(fragment)


def site_centre(fragment):
    p = re.compile("(CGS1|CGS2|CGS3|CGS4|PAC1|MPCC)")
    return p.match(fragment)


def process_fragment(fragment):
    fragment_parsers = [applicability_start, orbit_period, applicability_time_period, detector_id,
                        absolute_orbit_number, relative_orbit_number, tile_number, processing_baseline, band_index,
                        completeness_id, degradation]
    for parser in fragment_parsers:
        if parser(fragment):
            return parser.__name__, parser(fragment).group(1)


def get_filetype(the_match):
    # filetype: category + semantics
    return the_match.groups()[2] + the_match.groups()[3]

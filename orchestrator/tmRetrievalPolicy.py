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
from FileUtils import *


def getPolicies():
    policies = ["ValCover", "LatestValCover", "ValIntersect", "LatestValIntersect", "LatestValidityClosest",
                "BestCenteredCover", "LatestValCoverClosest", "LargestOverlap", "LargestOverlap85", "LatestValidity",
                "LatestValCoverNewestValidity"]
    return policies


def format_date_as_utc(a_date):
    import time
    timeString = time.strftime("%Y-%m-%dT%H:%M:%SZ", a_date)
    return timeString


def get_utc_date_from_utc_string(a_string):
    import time
    from time import mktime
    from datetime import datetime
    struct = time.strptime(a_string, "%Y-%m-%dT%H:%M:%SZ")
    dt = datetime.fromtimestamp(mktime(struct))
    return dt


def parse_date(a_date):
    import time
    from time import mktime
    from datetime import datetime

    if "T" in a_date:
        struct = time.strptime(a_date, "%Y%m%dT%H%M%S")
    else:
        struct = time.strptime(a_date, "%Y%m%d%H%M%S")
    dt = datetime.fromtimestamp(mktime(struct))
    return dt


def parse_period_date(a_dates):
    import time
    from time import mktime
    from datetime import datetime

    assert "_" in a_dates

    fragments = a_dates.split("_")
    begin = parse_date(fragments[0])
    end = parse_date(fragments[1])
    return (begin, end)


def parse_day(a_day):
    import time
    from time import mktime
    from datetime import datetime
    struct = time.strptime(a_day, "%Y%m%d")
    dt = datetime.fromtimestamp(mktime(struct))
    return dt


def parse_hour(an_hour):
    import time
    from time import mktime
    from datetime import datetime
    struct = time.strptime(an_hour, "%H%M%S")
    dt = datetime.fromtimestamp(mktime(struct))
    return dt


def mean_period(start, end):
    return start + ((end - start) / 2)


def tuple_to_dict(a_tuple_list):
    dict = {}
    for each in a_tuple_list:
        dict[each[0]] = each[1]
    return dict


class Policies(object):
    def __init__(self):
        pass

    def filter(self, a_criteria, an_iterable):
        pass


def get_validity_dates_from_file(file_name):
    dict = tuple_to_dict(parse_all(file_name))
    if "applicability_time_period" in dict:
        return parse_period_date(dict["applicability_time_period"])
    if "applicability_start" in dict:
        return (parse_date(dict["applicability_start"]),)
    return (None, None)


def get_mean_validity_dates_from_file(file_name):
    begin, end = get_validity_dates_from_file(file_name)
    if begin and end:
        return mean_period(begin, end)
    return None


def get_creation_date_from_file(file_name):
    dict = tuple_to_dict(parse_all(file_name))
    if "Creation_Date" in dict:
        return parse_date(dict["Creation_Date"])
    return None


def getValCover(file_list, t0, t1, dt0, dt1):
    """
    This mode gets all files that cover entirely time interval [t0 ? dt0, t1 + dt1]. Using this query in the scenario exhibited in fig B-1, it will return records R2 and R3
    """

    result = []

    for file in file_list:
        begin, end = get_validity_dates_from_file(file)
        if (begin <= t0 - dt0) and (end >= t1 + dt1):
            result.append(file)

    return result


def getLatestValCover(file_list, t0, t1, dt0, dt1):
    """
    This mode gets the latest file that covers entirely time interval [t0 ? dt0 , t1 + dt1]. The latest record is the one with the more
    recent Generation Date. Using this query in the scenario exhibited in fig B-1, it will return record R3
    """
    initial_result = getValCover(file_list, t0, t1, dt0, dt1)

    result = sorted(initial_result, key=get_creation_date_from_file)
    return result[-1]

    # sort by validation date


def getValIntersect(file_list, t0, t1, dt0, dt1):
    """
    This mode gets all files that cover partly time interval [t0 ? dt0 , t1 + dt1]. Using this query in the scenario exhibited in fig B-1, it
    will return records R1, R2, R3 and R4.
    """
    result = []

    for file in file_list:
        begin, end = get_validity_dates_from_file(file)
        if (begin <= t0 - dt0 <= end) or (begin <= t1 + dt1 <= end):
            result.append(file)

    return result


def getLatestValIntersect(file_list, t0, t1, dt0, dt1):
    """
    This mode gets the latest file that covers partly time interval [t0 ? dt0 , t1 + dt1]. The latest record is the one with the more recent
    Generation Date. Using this query in the scenario exhibited in fig B-1, it will return record R4
    """
    initial_result = getValIntersect(file_list, t0, t1, dt0, dt1)
    result = sorted(initial_result, key=get_creation_date_from_file)
    return result[-1]


def getLatestValidityClosest(file_list, t0, t1, dt0, dt1):
    """
    This mode gets the latest file which is nearest to ((t0-dt0)+(t1+dt1))/2. Using this query in the scenario exhibited in fig B-1, it will return record R4
    """
    results = []
    middle_time = mean_period(t0 - dt0, t1 + dt1)
    for file in file_list:
        start, end = get_validity_dates_from_file(file)
        if start >= middle_time:
            results.append(file)

    result = sorted(results, key=lambda x: get_validity_dates_from_file(x)[0] - middle_time)
    return result[0]


def getBestCenteredCover(file_list, t0, t1, dt0, dt1):
    """
    This mode gets the latest file which covers entirely time interval [t0 - dt0 , t1 + dt1], and for which is maximized the minimum
    distance of his extremes from the time interval borders. That is, if we name A and B the left and right endpoint of the file
    validity interval, the selected file is the one corresponding to maxi(min(Ai ? (t0 ? dt0 ), Bi ? (t1 + dt1 )). Using this query in
    the scenario exhibited in fig B-1, it will return record R3.
    """
    initial_result = getValCover(file_list, t0, t1, dt0, dt1)
    initial_result = sorted(file_list, key=get_creation_date_from_file, reverse=True)
    result = sorted(initial_result, key=lambda x: min(t0 - dt0 - get_validity_dates_from_file(x)[0],
                                                      get_validity_dates_from_file(x)[1] - t1 - dt1))
    return result[-1]


def getLatestValCoverClosest(file_list, t0, t1, dt0, dt1):
    """
    This mode gets the file that :
    * covers entirely time interval interval [t0 ? dt0 , t1 + dt1]
    and
    * has got the start time closest to to-dt0.
    Basically the outcomes of this mode is the same as the following sequence is applied:
    * Get files with ?ValCover? mode
    * Among the returned files select the one with start time closes to to-dt0.
    In Figure B-1 this would be product R2. If there are several files with the same start time choose the most recent ingestion time
    """
    initial_result = getValCover(file_list, t0, t1, dt0, dt1)
    initial_result = sorted(initial_result, key=get_creation_date_from_file, reverse=True)
    result = sorted(initial_result, key=lambda x: t0 - dt0 - get_validity_dates_from_file(x)[0])
    return result[0]


def getLargestOverlap(file_list, t0, t1, dt0, dt1):
    """
    This mode gets the file (only one) that satisfies both the following conditions:
    * covers entirely time interval interval [t0 ? dt0 , t1 + dt1]
    * has got the largest overlap.
    Basically the outcomes of this mode is the same as the following sequence is applied:
    * Get files with ?ValCover? mode
    * Among the returned files select the one with the largest overlap.
    If there are several products with the same overlap (e.g. full coverage), the product with the start time that is closest to TOTO
    is chosen. Note that in the full coverage case the result is identical to "ValCoverClosest".
    """
    initial_result = getValCover(file_list, t0, t1, dt0, dt1)
    initial_result = sorted(file_list, key=get_creation_date_from_file, reverse=True)
    if initial_result:
        return getLatestValCoverClosest(file_list, t0, t1, dt0, dt1)
    # todo calculate % of overlap...


def getLargestOverlap85(file_list, t0, t1, dt0, dt1):
    """
    This mode is the same as LargestOverlap but only products with at least 85% coverage of the query interval are selected.
    """
    pass


def getLatestValidity(file_list, t0, t1, dt0, dt1):
    """
    This mode gets a product with the latest Validity Start Time. In Figure B-1 this would be product R6.
    """
    initial_result = sorted(file_list, key=lambda x: get_validity_dates_from_file(x)[0])
    return initial_result[-1]


def getLatestValCoverNewestValidity(file_list, t0, t1, dt0, dt1):
    """
    This mode applies first ?LatestValCover?. If no file is returned then it applies "Latest Validity"
    """

    initial_result = getLatestValCover(file_list, t0, t1, dt0, dt1)
    if not initial_result:
        return getLatestValidity(file_list, t0, t1, dt0, dt1)
    return initial_result


def getLatestByCreationDate(file_list, t0, t1, dt0, dt1):
    return sorted(file_list, key=get_creation_date_from_file, reverse=True)[0]

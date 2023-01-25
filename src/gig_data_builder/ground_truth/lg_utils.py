import json
import os

from utils.cache import cache

from gig_data_builder._common.FuzzySearch import FuzzySearch
from gig_data_builder._constants import DIR_REGION_ID_MAP
from gig_data_builder._utils import log

from utils import JSONFile


def get_lg_id_to_name_and_gnd_to_lg():
    lg_id_to_name = JSONFile('data_group_truth/lg/lg_id_to_lg_name.json').read()
    gnd_to_lg = JSONFile('data_group_truth/lg/gnd_id_to_lg_id.json').read()

    return (lg_id_to_name, gnd_to_lg)
    

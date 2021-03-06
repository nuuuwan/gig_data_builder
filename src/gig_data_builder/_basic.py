import os

from fuzzywuzzy import process
from utils import tsv

from gig_data_builder._constants import DIR_DATA
from gig_data_builder._utils import log


def get_basic_data_file(region_type):
    return os.path.join(DIR_DATA, f'{region_type}.tsv')


def get_basic_data(region_type):
    basic_data_file = get_basic_data_file(region_type)
    return tsv.read(basic_data_file)


def store_basic_data(region_type, data_list):
    basic_data_file = get_basic_data_file(region_type)
    tsv.write(basic_data_file, data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {basic_data_file}')


def get_parent_to_field_to_ids(region_type, parent_region_type, field_key):
    get_basic_data(region_type)
    if parent_region_type is not None:
        field_key_parent_id = parent_region_type + '_id'
    else:
        parent_id = 'LK'

    parent_to_field_to_ids = {}
    for d in get_basic_data(region_type):
        id = d['id']
        if parent_region_type is not None:
            parent_id = d[field_key_parent_id]
        field_value = d[field_key]

        if parent_id not in parent_to_field_to_ids:
            parent_to_field_to_ids[parent_id] = {}
        if field_value not in parent_to_field_to_ids[parent_id]:
            parent_to_field_to_ids[parent_id][field_value] = []
        parent_to_field_to_ids[parent_id][field_value].append(id)
    return parent_to_field_to_ids


def fuzzy_match(cand_field_value, field_to_ids):
    if cand_field_value == '':
        return None

    field_values = field_to_ids.keys()
    matches = process.extract(cand_field_value, field_values, limit=1)
    if matches:
        matching_field_value = matches[0][0]
        return field_to_ids[matching_field_value][0]
    return None

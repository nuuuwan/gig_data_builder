import json
import os
import random

from fuzzywuzzy import process
from utils import tsv

from gig_data_builder._constants import DIR_REGION_ID_MAP
from gig_data_builder._utils import log
from gig_data_builder.basic_data import get_basic_data


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
        log.error('Invalid cand_field_value: %s', cand_field_value)
        log.error(list(field_to_ids.items())[0])
        return None

    field_values = field_to_ids.keys()
    matches = process.extract(cand_field_value, field_values, limit=1)
    if matches:
        matching_field_value = matches[0][0]
        return field_to_ids[matching_field_value][0]
    return None


def build_map_data_list():
    raw_map_file = os.path.join(
        DIR_REGION_ID_MAP, '00-Data_PD_LA_DSD_Ward_GND.tsv'
    )
    raw_map_data = tsv.read(raw_map_file)

    parent_to_province_name_to_ids = get_parent_to_field_to_ids(
        'province', None, 'name'
    )
    parent_to_district_name_to_ids = get_parent_to_field_to_ids(
        'district', 'province', 'name'
    )
    parent_to_dsd_name_to_ids = get_parent_to_field_to_ids(
        'dsd', 'district', 'name'
    )
    parent_to_gnd_name_to_ids = get_parent_to_field_to_ids(
        'gnd', 'dsd', 'name'
    )
    parent_to_gnd_num_to_ids = get_parent_to_field_to_ids(
        'gnd', 'dsd', 'gnd_num'
    )

    parent_to_pd_name_to_ids = get_parent_to_field_to_ids(
        'pd', 'district', 'name'
    )

    def map_map_data(d):
        """
        {
            'Index': '1',
            'PROVINCE_N': 'Eastern',
            'DISTRICT_N': 'Ampara',
            'Polling_D': 'Potuvil',
            'DSD_N': 'Addalachchenai',
            'Local_Gov': 'Addalachchenai PS',
            'Ward': 'Arafa',
            'Type_Ward': '',
            'GND_N': 'Addalachchenai 01',
            'GND_NO': 'AD/33',
            'Votes': '772',
            'TOT_POP': '1108',
            'E_Sinhales': '13',
            'E_SLTamil': '0',
            'E_IndTamil': '2',
            'E_SLMoor': '1108',
            'E_Burgher': '0',
            'E_Malay': '0',
            'E_SLChetty': '0',
            'E_Bharatha': '0',
            'E_Other': '0',
            'E_AllTamil': '2',
            'E_AllOther': '0'
        }
        """

        country_id = 'LK'
        province_id = fuzzy_match(
            d['PROVINCE_N'],
            parent_to_province_name_to_ids[country_id],
        )

        district_id = fuzzy_match(
            d['DISTRICT_N'],
            parent_to_district_name_to_ids[province_id],
        )

        dsd_id = fuzzy_match(
            d['DSD_N'],
            parent_to_dsd_name_to_ids[district_id],
        )

        gnd_id = fuzzy_match(
            d['GND_N'],
            parent_to_gnd_name_to_ids[dsd_id],
        )

        if gnd_id is None:
            gnd_id = fuzzy_match(
                d['GND_NO'],
                parent_to_gnd_num_to_ids[dsd_id],
            )

        if gnd_id is None:
            log.error('Could not find gnd_id for: %s', json.dumps(d))


        pd_id = fuzzy_match(
            d['Polling_D'],
            parent_to_pd_name_to_ids[district_id],
        )

        if pd_id is None:
            log.error('Could not find pd_id for: %s', json.dumps(d))
            ed_id = None
        else:
            ed_id = pd_id[:5]

        new_d = {
            'country_id': country_id,
            'province_id': province_id,
            'district_id': district_id,
            'dsd_id': dsd_id,
            'gnd_id': gnd_id,
            'pd_id': pd_id,
            'ed_id': ed_id,
        }

        if random.random() < 1 / 1000:
            print(d['Index'], new_d)

        return new_d

    cleaned_map_data = list(
        map(
            map_map_data,
            raw_map_data,
        )
    )
    return cleaned_map_data


if __name__ == '__main__':
    build_map_data_list()

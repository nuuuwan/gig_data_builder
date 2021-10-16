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
import json
import os

from fuzzywuzzy import process
from utils import tsv

from gig_data_builder._constants import DIR_DATA, DIR_REGION_ID_MAP
from gig_data_builder._utils import log
from gig_data_builder.basic_data import get_basic_data

REGION_ID_MAP_FILE = os.path.join(
    DIR_DATA,
    'region_id_map.tsv',
)

FIXED_REGION_ID_MAP_FILE = os.path.join(
    DIR_DATA,
    'region_id_map.fixed.tsv',
)


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


def build_map_data_list_list():
    raw_map_file = os.path.join(
        DIR_REGION_ID_MAP, '00-Data_PD_LA_DSD_Ward_GND.tsv'
    )
    raw_map_data_list = tsv.read(raw_map_file)

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

    def map_map_data_list(d):
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
            log.error('Could not find pd_id for gnd: %s', gnd_id)
            ed_id = None
        else:
            ed_id = pd_id[:5]

        new_d = {
            'country_id': country_id,
            'province_id': province_id,
            'district_id': district_id,
            'dsd_id': dsd_id,
            'gnd_id': gnd_id,

            'ed_id': ed_id,
            'pd_id': pd_id,
            'source_type': 'original',

        }
        return new_d

    cleaned_map_data_list = sorted(
        list(
            map(
                map_map_data_list,
                raw_map_data_list,
            )
        ),
        key=lambda d: d['gnd_id'],
    )

    n_cleaned_map_data_list = len(cleaned_map_data_list)
    tsv.write(REGION_ID_MAP_FILE, cleaned_map_data_list)
    log.info(f'Wrote {n_cleaned_map_data_list} rows to {REGION_ID_MAP_FILE}')


def fix_missing_values():
    cleaned_map_data_list = tsv.read(REGION_ID_MAP_FILE)
    all_gnd_ids = set(map(lambda d: d['gnd_id'], get_basic_data('gnd')))
    dsd_to_pds_to_n = {}
    gnds_without_pds = set()
    map_gnd_ids = set()
    new_fixed_data_index = {}
    for d in cleaned_map_data_list:
        gnd_id = d['gnd_id']
        map_gnd_ids.add(gnd_id)
        dsd_id = d['dsd_id']
        pd_id = d['pd_id']

        if pd_id is None:
            gnds_without_pds.add(gnd_id)
        else:
            if dsd_id not in dsd_to_pds_to_n:
                dsd_to_pds_to_n[dsd_id] = {}
            if pd_id not in dsd_to_pds_to_n[dsd_id]:
                dsd_to_pds_to_n[dsd_id][pd_id] = 0
            dsd_to_pds_to_n[dsd_id][pd_id] += 1

        new_fixed_data_index[gnd_id] = d

    map_not_all = map_gnd_ids.difference(all_gnd_ids)
    assert len(map_not_all) == 0

    all_not_map = all_gnd_ids.difference(map_gnd_ids)

    # fix gnds without map rows or incorrect pds by using dsd row
    country_id = 'LK'
    for gnd_id in list(all_not_map) + list(gnds_without_pds):
        dsd_id = gnd_id[:7]
        pd_id = sorted(
            dsd_to_pds_to_n.get(dsd_id).items(),
            key=lambda x: -x[1],
        )[0][0]
        ed_id = pd_id[:5]

        district_id = dsd_id[:5]
        province_id = district_id[:4]

        new_d = {
            'country_id': country_id,
            'province_id': province_id,
            'district_id': district_id,
            'dsd_id': dsd_id,
            'gnd_id': gnd_id,
            'pd_id': pd_id,
            'ed_id': ed_id,
            'source_type': 'fixed',
        }
        new_fixed_data_index[gnd_id] = new_d

    new_fixed_data_list = sorted(
        new_fixed_data_index.values(),
        key=lambda x: x['gnd_id'],
    )
    fixed_map_data_list = new_fixed_data_list
    n_fixed_map_data_list = len(fixed_map_data_list)
    tsv.write(FIXED_REGION_ID_MAP_FILE, fixed_map_data_list)
    log.info(
        f'Wrote {n_fixed_map_data_list} rows to {FIXED_REGION_ID_MAP_FILE}'
    )

if __name__ == '__main__':
    # build_map_data_list_list()
    fix_missing_values()

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

from utils import tsv

from gig_data_builder._constants import DIR_DATA, DIR_REGION_ID_MAP
from gig_data_builder._utils import log
from gig_data_builder.basic_data import (fuzzy_match, get_basic_data,
                                         get_basic_data_file,
                                         get_parent_to_field_to_ids)
from gig_data_builder.build_from_moh import MOH_REGION_ID_MAP

REGION_ID_MAP_FILE = os.path.join(
    DIR_DATA,
    'region_id_map.tsv',
)

EXPANDED_REGION_ID_MAP_FILE = os.path.join(
    DIR_DATA,
    'region_id_map.expanded.tsv',
)

FINAL_REGION_ID_MAP_FILE = os.path.join(
    DIR_DATA,
    'region_id_map.final.tsv',
)


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
            'lg_name': d['Local_Gov'],
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


def expand():
    # Fix missing values
    cleaned_map_data_list = tsv.read(REGION_ID_MAP_FILE)
    all_gnd_ids = set(map(lambda d: d['gnd_id'], get_basic_data('gnd')))
    dsd_to_pd_to_n = {}
    dsd_to_lg_to_n = {}
    gnds_without_pds = set()
    map_gnd_ids = set()
    new_fixed_data_index = {}
    for d in cleaned_map_data_list:
        gnd_id = d['gnd_id']
        map_gnd_ids.add(gnd_id)
        dsd_id = d['dsd_id']
        pd_id = d['pd_id']
        lg_name = d['lg_name']

        if pd_id is None:
            gnds_without_pds.add(gnd_id)
        else:
            if dsd_id not in dsd_to_pd_to_n:
                dsd_to_pd_to_n[dsd_id] = {}
            if pd_id not in dsd_to_pd_to_n[dsd_id]:
                dsd_to_pd_to_n[dsd_id][pd_id] = 0
            dsd_to_pd_to_n[dsd_id][pd_id] += 1

        if dsd_id not in dsd_to_lg_to_n:
            dsd_to_lg_to_n[dsd_id] = {}
        if lg_name not in dsd_to_lg_to_n[dsd_id]:
            dsd_to_lg_to_n[dsd_id][lg_name] = 0
        dsd_to_lg_to_n[dsd_id][lg_name] += 1

        new_fixed_data_index[gnd_id] = d

    map_not_all = map_gnd_ids.difference(all_gnd_ids)
    assert len(map_not_all) == 0

    all_not_map = all_gnd_ids.difference(map_gnd_ids)

    # fix gnds without map rows or incorrect pds by using dsd row
    country_id = 'LK'
    for gnd_id in list(all_not_map) + list(gnds_without_pds):
        dsd_id = gnd_id[:7]
        pd_id = sorted(
            dsd_to_pd_to_n.get(dsd_id).items(),
            key=lambda x: -x[1],
        )[0][0]
        lg_name = sorted(
            dsd_to_lg_to_n.get(dsd_id).items(),
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
            'lg_name': lg_name,
            'source_type': 'fixed',
        }
        new_fixed_data_index[gnd_id] = new_d

    new_fixed_data_list = sorted(
        new_fixed_data_index.values(),
        key=lambda x: x['gnd_id'],
    )

    # expand with lg_ids
    lg_name_to_lg_id = {}
    district_to_n = {}

    def expand_lg_ids(d):
        lg_name = d['lg_name']
        if lg_name not in lg_name_to_lg_id:
            district_id = d['district_id']
            if district_id not in district_to_n:
                district_to_n[district_id] = 0
            district_to_n[district_id] += 1
            district_id_end = district_id[-2:]
            lg_id = 'LG-%s%03d' % (district_id_end, district_to_n[district_id])
            lg_name_to_lg_id[lg_name] = lg_id
        d['lg_id'] = lg_name_to_lg_id[lg_name]
        return d

    expanded_data_list = list(map(expand_lg_ids, new_fixed_data_list))

    # store
    n_expanded_data_list = len(expanded_data_list)
    tsv.write(EXPANDED_REGION_ID_MAP_FILE, expanded_data_list)
    log.info(
        f'Wrote {n_expanded_data_list} rows to {EXPANDED_REGION_ID_MAP_FILE}'
    )


def build_basic_lg_data():
    expanded_data_list = tsv.read(EXPANDED_REGION_ID_MAP_FILE)
    lg_id_to_d = {}
    for d in expanded_data_list:
        lg_id = d['lg_id']
        lg_name = d['lg_name']
        if lg_id not in lg_id_to_d:
            lg_id_to_d[lg_id] = {
                'id': lg_id,
                'lg_id': lg_id,
                'name': lg_name,
            }
    basic_data_list = sorted(
        lg_id_to_d.values(),
        key=lambda d: d['lg_id'],
    )
    n_basic_data_list = len(basic_data_list)
    basic_data_file = get_basic_data_file('lg')

    tsv.write(basic_data_file, basic_data_list)
    log.info(f'Wrote {n_basic_data_list} rows to {basic_data_file}')


def combine_expanded_and_moh():
    moh_data_list = tsv.read(MOH_REGION_ID_MAP)
    gnd_to_moh = dict(
        list(
            map(
                lambda d: (d['gnd_id'], d['moh_id']),
                moh_data_list,
            )
        )
    )
    expanded_data_list = tsv.read(EXPANDED_REGION_ID_MAP_FILE)

    def combine(d):
        d['moh_id'] = gnd_to_moh.get(d['gnd_id'], None)
        return d

    combined_data_list = sorted(
        list(map(combine, expanded_data_list)), key=lambda d: d['gnd_id']
    )
    n_combined_data_list = len(combined_data_list)
    tsv.write(FINAL_REGION_ID_MAP_FILE, combined_data_list)
    log.info(
        f'Wrote {n_combined_data_list} rows to {FINAL_REGION_ID_MAP_FILE}'
    )


def get_region_id_index():
    data_list = tsv.read(FINAL_REGION_ID_MAP_FILE)
    return dict(zip(
        list(map(lambda d: d['gnd_id'], data_list)),
        data_list,
    ))


if __name__ == '__main__':
    build_map_data_list_list()
    expand()
    build_basic_lg_data()
    combine_expanded_and_moh()

import json
import os

from utils import tsv

from gig_data_builder._basic import (get_basic_data, get_basic_data_file,
                                     store_basic_data)
from gig_data_builder._common.FuzzySearch import FuzzySearch
from gig_data_builder._constants import DIR_REGION_ID_MAP, DIR_TMP
from gig_data_builder._utils import log
from gig_data_builder.regions.moh_basic_and_region_id_map import \
    MOH_REGION_ID_MAP

REGION_ID_MAP_FILE = os.path.join(
    DIR_TMP,
    'region_id_map.tsv',
)

EXPANDED_REGION_ID_MAP_FILE = os.path.join(
    DIR_TMP,
    'region_id_map.expanded.tsv',
)


def clean(x, fs):
    [i, d] = x
    if (i + 1) % 1_000 == 0:
        gnd_name = d['GND_N']
        log.debug(f'{i + 1}) Cleaning {gnd_name}')
    country_id = 'LK'
    province_id = fs.search(
        None,
        country_id,
        'province',
        'name',
        d['PROVINCE_N'],
    )
    district_id = fs.search(
        'province',
        province_id,
        'district',
        'name',
        d['DISTRICT_N'],
    )

    dsd_id = fs.search(
        'district',
        district_id,
        'dsd',
        'name',
        d['DSD_N'],
    )

    gnd_id = fs.search(
        'dsd',
        dsd_id,
        'gnd',
        'name',
        d['GND_N'],
    )

    if gnd_id is None:
        gnd_id = fs.search(
            'dsd',
            dsd_id,
            'gnd',
            'name_num',
            d['GND_NO'],
        )

    if gnd_id is None:
        log.error('Could not find gnd_id for: %s', json.dumps(d))

    pd_id = fs.search(
        'district',
        district_id,
        'pd',
        'name',
        d['Polling_D'],
    )

    if pd_id is None:
        # Jaffna Electoral District (EC-10) special cases ???
        if dsd_id == 'LK-4112':
            pd_id = 'EC-10C'
        elif dsd_id == 'LK-4127':
            pd_id = 'EC-10G'
        elif dsd_id == 'LK-4124':
            pd_id = 'EC-10G'
        else:
            log.error('Could not find pd_id for gnd: %s', gnd_id)

    if pd_id is None:
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


def build_map_data_list_list():
    raw_map_file = os.path.join(
        DIR_REGION_ID_MAP, '00-Data_PD_LA_DSD_Ward_GND.tsv'
    )
    raw_map_data_list = tsv.read(raw_map_file)

    fs = FuzzySearch()

    cleaned_map_data_list = sorted(
        list(
            map(
                lambda x: clean(x, fs),
                enumerate(raw_map_data_list),
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

    basic_data = get_basic_data('_tmp/precensus-', 'gnd')
    all_gnd_ids = set(map(lambda d: d['gnd_id'], basic_data))

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
            lg_id = 'LG-%s%03d' % (
                district_id_end,
                district_to_n[district_id],
            )
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
    store_basic_data('_tmp/precensus-pregeo-', 'lg', basic_data_list)


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
    region_id_map_file = get_basic_data_file(
        '_tmp/precensus-', 'region_id_map'
    )
    tsv.write(region_id_map_file, combined_data_list)
    log.info(f'Wrote {n_combined_data_list} rows to {region_id_map_file}')


def get_region_id_index():
    region_id_map_file = get_basic_data_file('ents/', 'region_id_map')
    if not os.path.exists(region_id_map_file):
        region_id_map_file = get_basic_data_file(
            '_tmp/precensus-', 'region_id_map'
        )

    data_list = tsv.read(region_id_map_file)
    return dict(
        zip(
            list(map(lambda d: d['gnd_id'], data_list)),
            data_list,
        )
    )


def main():
    build_map_data_list_list()
    expand()
    build_basic_lg_data()
    combine_expanded_and_moh()


if __name__ == '__main__':
    main()

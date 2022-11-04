import json
import os

from utils import tsv
from utils.cache import cache

from gig_data_builder._common.FuzzySearch import FuzzySearch
from gig_data_builder._constants import DIR_REGION_ID_MAP
from gig_data_builder._utils import log


def get_gnd_and_lg_name(d, fs):
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
        return None

    return [gnd_id, d['Local_Gov']]


@cache('get_gnd_id_to_lg_name', 3600)
def get_gnd_id_to_lg_name():
    raw_map_file = os.path.join(
        DIR_REGION_ID_MAP, '00-Data_PD_LA_DSD_Ward_GND.tsv'
    )
    raw_map_data_list = tsv.read(raw_map_file)

    fs = FuzzySearch()
    gnd_id_to_lg_name = {}
    n = len(raw_map_data_list)
    for i, d in enumerate(raw_map_data_list):
        x = get_gnd_and_lg_name(d, fs)
        if x == 0:
            continue
        [gnd_id, lg_name] = x
        gnd_id_to_lg_name[gnd_id] = lg_name
        if (i + 1) % 1_000 == 0:
            log.debug(f'{i + 1}/{n}) get_gnd_id_to_lg_name: {gnd_id}')

    return gnd_id_to_lg_name


def get_lg_id_to_name_and_gnd_to_lg():
    gnd_id_to_lg_name = get_gnd_id_to_lg_name()
    gnd_to_lg = {}
    district_to_lg_names_to_id = {}
    lg_id_to_name = {}
    for gnd_id, lg_name in gnd_id_to_lg_name.items():
        district_id = gnd_id[:5]

        if lg_name not in district_to_lg_names_to_id.get(district_id, {}):
            if district_id not in district_to_lg_names_to_id:
                district_to_lg_names_to_id[district_id] = {}

            n = len(district_to_lg_names_to_id[district_id].values()) + 1
            district_id_num = district_id[3:]
            lg_id = f'LG-{district_id_num}{n:03}'
            lg_id_to_name[lg_id] = lg_name
            district_to_lg_names_to_id[district_id][lg_name] = lg_id
        else:
            lg_id = district_to_lg_names_to_id[district_id][lg_name]

        gnd_to_lg[gnd_id] = lg_id
    return lg_id_to_name, gnd_to_lg

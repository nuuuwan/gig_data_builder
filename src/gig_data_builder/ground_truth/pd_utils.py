import json
import os

from utils import TSVFile
from utils import cache

from gig_data_builder._common.FuzzySearch import FuzzySearch
from gig_data_builder._constants import DIR_REGION_ID_MAP
from gig_data_builder._utils import log


def get_gnd_and_pd(d, fs):
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

    pd_id = fs.search(
        'province',
        province_id,
        'pd',
        'name',
        d['Polling_D'],
    )

    if pd_id is None:
        log.error('Could not find gnd_id for: %s', json.dumps(d))
        return None

    return [gnd_id, pd_id]


@cache('get_gnd_to_pd', 3600)
def get_gnd_to_pd():
    raw_map_file = os.path.join(
        DIR_REGION_ID_MAP, '00-Data_PD_LA_DSD_Ward_GND.tsv'
    )
    raw_map_data_list = TSVFile(raw_map_file).read()

    fs = FuzzySearch()
    n = len(raw_map_data_list)
    gnd_to_pd = {}
    for i, d in enumerate(raw_map_data_list):
        x = get_gnd_and_pd(d, fs)
        if not x:
            continue
        [gnd_id, pd_id] = x
        gnd_to_pd[gnd_id] = pd_id
        if (i + 1) % 1_000 == 0:
            log.debug(f'{i + 1}/{n}) get_gnd_to_pd: {gnd_id}')

    return gnd_to_pd

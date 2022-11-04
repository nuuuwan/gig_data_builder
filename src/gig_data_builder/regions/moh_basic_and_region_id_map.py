import json
import os

import geopandas
from utils import tsv

from gig_data_builder import _utils
from gig_data_builder._basic import (fuzzy_match, get_parent_to_field_to_ids,
                                     store_basic_data)
from gig_data_builder._constants import DIR_MOH, DIR_TMP
from gig_data_builder._utils import log

MOH_GEOJSON_FILE = os.path.join(DIR_TMP, 'SL_MOH_GN.geo.json')
MOH_REGION_ID_MAP = os.path.join(DIR_TMP, 'moh.region_id_map.tsv')
PREFIX = '_tmp/precensus-pregeo-'


def convert_shp_to_geojson():
    moh_shp_file = os.path.join(DIR_MOH, 'SL_MOH_GN.shp')
    df = geopandas.read_file(moh_shp_file)
    df.to_file(MOH_GEOJSON_FILE, driver='GeoJSON')
    log.info(f'Converted {moh_shp_file} to {MOH_GEOJSON_FILE}')


def get_raw_moh_data_list():
    df = geopandas.read_file(MOH_GEOJSON_FILE)
    return df.to_dict('records')

def parse():
    data_list = get_raw_moh_data_list()

    parent_to_gnd_num_to_ids = get_parent_to_field_to_ids(
        'gnd', 'district', 'gnd_num'
    )

    moh_data_list = []
    n_data_list = len(data_list)
    moh_name_to_id = {}
    district_to_n = {}
    moh_to_district = {}
    for i, d in enumerate(data_list):
        if not d['GND_NO']:
            continue

        province_id = 'LK-%s' % (d['PROVINCE_C'])
        district_id = '%s%s' % (province_id, d['DISTRICT_C'])
        gnd_num = d['GND_NO'].replace(' ', '')

        gnd_id = fuzzy_match(gnd_num, parent_to_gnd_num_to_ids[district_id])
        dsd_id = None
        if gnd_id is not None:
            dsd_id = gnd_id[:7]
        else:
            log.error('Could not find GND_ID for gnd_num: %s', gnd_num)

        moh_name = d['MOH_N']

        if moh_name not in moh_name_to_id:
            if district_id not in district_to_n:
                district_to_n[district_id] = 0
            district_to_n[district_id] += 1
            district_num = district_id[-2:]
            moh_id = 'MOH-%s%03d' % (district_num, district_to_n[district_id])
            moh_name_to_id[moh_name] = moh_id
        moh_id = moh_name_to_id[moh_name]

        if moh_id not in moh_to_district:
            moh_to_district[moh_id] = set()
        moh_to_district[moh_id].add(district_id)

        moh_d = {
            'province_id': province_id,
            'district_id': district_id,
            'dsd_id': dsd_id,
            'gnd_id': gnd_id,
            'moh_name': moh_name,
            'moh_id': moh_id,
        }
        if (i + 1) % 1000 == 0:
            log.debug(f'{ i + 1 }/{n_data_list}: {json.dumps(moh_d)}')
        moh_data_list.append(moh_d)

    moh_data_list = sorted(
        moh_data_list,
        key=lambda d: d['gnd_id'],
    )

    tsv.write(MOH_REGION_ID_MAP, moh_data_list)
    n_moh_data_list = len(moh_data_list)
    log.info(f'Wrote {n_moh_data_list} rows to {MOH_REGION_ID_MAP}')


def extract_moh_d(d):
    moh_id = d['moh_id']
    return {
        'id': moh_id,
        'moh_id': moh_id,
        'name': d['moh_name'],
    }


def build_basic_moh_data():
    moh_data_list = tsv.read(MOH_REGION_ID_MAP)
    basic_data_list = sorted(
        _utils.dedupe(
            map(
                extract_moh_d,
                moh_data_list,
            ),
            func_key=lambda d: d['id'],
        ),
        key=lambda d: d['id'],
    )
    store_basic_data(PREFIX, 'moh', basic_data_list)


def main():
    # convert_shp_to_geojson()
    parse()
    # build_basic_moh_data()


if __name__ == '__main__':
    main()

import os

import geopandas

from gig_data_builder import _basic
from gig_data_builder._common.FuzzySearch import FuzzySearch
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


def get_moh_id_to_name_and_gnd_to_moh_and_moh_to_district():
    log.debug('get_moh_id_to_name_and_gnd_to_moh_and_moh_to_district')
    data_list = get_raw_moh_data_list()

    fs = FuzzySearch()

    moh_name_to_id = {}  # repetition
    district_to_n = {}  # for numbering
    moh_id_to_name = {}
    gnd_to_moh = {}
    moh_to_district = {}
    n = len(data_list)
    for i, d in enumerate(data_list):
        if not d['GND_NO']:
            continue

        province_id = 'LK-%s' % (d['PROVINCE_C'])
        district_id = '%s%s' % (province_id, d['DISTRICT_C'])
        gnd_num = d['GND_NO'].replace(' ', '')

        gnd_id = fs.search(
            'district',
            district_id,
            'gnd',
            'gnd_num',
            gnd_num,
        )
        if (i + 1) % 1_000 == 0:
            log.debug(f'{i + 1}/{n}) Processing MOH for GND: {gnd_id}')

        moh_name = d['MOH_N']

        if moh_name not in moh_name_to_id:
            if district_id not in district_to_n:
                district_to_n[district_id] = 0
            district_to_n[district_id] += 1
            district_num = district_id[-2:]
            moh_id = 'MOH-%s%03d' % (district_num, district_to_n[district_id])
            moh_name_to_id[moh_name] = moh_id
        moh_id = moh_name_to_id[moh_name]

        moh_id_to_name[moh_id] = moh_name
        gnd_to_moh[gnd_id] = moh_id
        moh_to_district[moh_id] = district_id

    return [
        moh_id_to_name,
        gnd_to_moh,
        moh_to_district,
    ]


def add_moh_to_gnd(gnd_to_moh):
    gnd_data_list = _basic.get_basic_data(
        '_tmp/premoh-prelg-precensus', 'gnd'
    )
    gnd_data_list2 = []
    n = len(gnd_data_list)
    n_missing = 0
    for d in gnd_data_list:
        moh_id = gnd_to_moh.get(d['gnd_id'], None)
        if not moh_id:
            n_missing += 1
        d['moh_id'] = moh_id
        gnd_data_list2.append(d)
    _basic.store_basic_data('_tmp/prelg-precensus', 'gnd', gnd_data_list2)
    log.warning(f'No MOH for {n_missing}/{n} GNDs')


def build_precensus_pregeo_moh(moh_id_to_name, moh_to_district):
    district_data_index = _basic.get_basic_data_index(
        '_tmp/precensus-', 'district'
    )
    moh_data_list = []
    for moh_id, moh_name in moh_id_to_name.items():
        district_id = moh_to_district[moh_id]
        district = district_data_index[district_id]
        d = {
            'id': moh_id,
            'moh_id': moh_id,
            'name': moh_name,
            'province_id': district['province_id'],
            'district_id': district_id,
            'ed_id': district['ed_id'],
        }
        moh_data_list.append(d)
    _basic.store_basic_data('_tmp/precensus-pregeo-', 'moh', moh_data_list)


def main():
    convert_shp_to_geojson()
    [
        moh_id_to_name,
        gnd_to_moh,
        moh_to_district,
    ] = get_moh_id_to_name_and_gnd_to_moh_and_moh_to_district()
    add_moh_to_gnd(gnd_to_moh)
    build_precensus_pregeo_moh(moh_id_to_name, moh_to_district)


if __name__ == '__main__':
    main()

import os

import geopandas

from gig_data_builder._common.FuzzySearch import FuzzySearch
from gig_data_builder._constants import DIR_MOH
from gig_data_builder._utils import log
from gig_data_builder.base.StoredVariable import StoredVariable


def convert_shp_to_geojson():
    moh_shp_file = os.path.join(DIR_MOH, 'SL_MOH_GN.shp')
    df = geopandas.read_file(moh_shp_file)
    return df


def get_raw_moh_data_list():
    df = convert_shp_to_geojson()
    return df.to_dict('records')


def get_moh_data_file_path():
    return os.path.join('data_ground_truth', 'moh', 'moh_data.json')


def get_moh_data_hot():
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


var_moh_data = StoredVariable('moh_data', get_moh_data_hot)


def get_moh_id_to_name_and_gnd_to_moh_and_moh_to_district():
    return var_moh_data.get()

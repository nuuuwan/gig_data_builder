"""
{
  "PROVINCE_N": "CENTRAL",
  "PROVINCE_C": "2",
  "DISTRICT_N": "NUWARA ELIYA",
  "DISTRICT_C": "3",
  "DSD_N": "HANGURANKETHA",
  "DSD_C": null,
  "GND_NO": "481 B",
  "GND_N": "Deniyagama",
  "GND_C": "490",
  "MC_UC_PS_N": "Hanguranketha PS",
  "AREA": 1869314.01398,
  "GN_UID": null,
  "ORIG_FID": 0,
  "Shape_Leng": 7138.80311174,
  "Shape_Le_1": 7138.80311174,
  "Shape_Area": 1869314.01398,
  "DIST_N2": null,
  "MOH_N": "MATHURATA",
  "OBJECTID": 0,
  "Shape_Le_2": 0.0
}
"""
import json
import os

import geopandas
from utils import tsv

from gig_data_builder._constants import DIR_DATA, DIR_MOH
from gig_data_builder._utils import log
from gig_data_builder.basic_data import fuzzy_match, get_parent_to_field_to_ids

MOH_GEOJSON_FILE = os.path.join(DIR_DATA, 'SL_MOH_GN.geo.json')
MOH_DATA_FILE = os.path.join(DIR_DATA, 'moh.tsv')


def convert_shp_to_geojson():
    moh_shp_file = os.path.join(DIR_MOH, 'SL_MOH_GN.shp')
    df = geopandas.read_file(moh_shp_file)
    df.to_file(MOH_GEOJSON_FILE, driver='GeoJSON')
    log.info(f'Converted {moh_shp_file} to {MOH_GEOJSON_FILE}')


def parse():
    df = geopandas.read_file(MOH_GEOJSON_FILE)
    data_list = df.to_dict('records')

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
        if i % 1000 == 0:
            log.info('%d/%d: %s', i, n_data_list, json.dumps(moh_d))
        moh_data_list.append(moh_d)

    for moh, districts in moh_to_district.items():
        if len(districts) > 1:
            print(moh, districts)

    moh_data_list = sorted(
        moh_data_list,
        key=lambda d: d['gnd_id'],
    )

    tsv.write(MOH_DATA_FILE, moh_data_list)
    n_moh_data_list = len(moh_data_list)
    log.info(f'Wrote {n_moh_data_list} rows to {MOH_DATA_FILE}')


if __name__ == '__main__':
    # convert_shp_to_geojson()
    parse()

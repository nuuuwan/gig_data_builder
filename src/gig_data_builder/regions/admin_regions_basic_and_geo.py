import json
import os

import geopandas

from gig_data_builder._basic import store_basic_data
from gig_data_builder._constants import DIR_STATSL_SHAPE
from gig_data_builder.regions._geo import save_geo

REGION_TYPE_TO_ID_LEN = {
    'province': 4,
    'district': 5,
    'dsd': 7,
}


def get_parent_ids_idx(region_id):
    n_region_id = len(region_id)
    d = {}
    for parent_type, n_parent_id in REGION_TYPE_TO_ID_LEN.items():
        if n_region_id >= n_parent_id:
            d[parent_type + '_id'] = region_id[:n_parent_id]
    return d


REGION_CONFIG_IDX = {
    "province": {
        'file_only': 'Provinces.json',
        'id_base_key': 'prov_c',
        'name_key': 'prov_n',
    },
    "district": {
        'file_only': 'Districts.json',
        'id_base_key': 'dis_c',
        'name_key': 'dis_n',
    },
    "dsd": {
        'file_only': 'DSDivisions.json',
        'id_base_key': 'dsd_c',
        'name_key': 'dsd_n',
    },
    "gnd": {
        'file_only': 'GNDivisions.json',
        'id_base_key': 'code',
        'name_key': 'name',
        'other_fields_key_map': {'gnd_num': 'gnnum'},
    },
}


def get_centroid(d):
    shape = d['geometry']
    lng, lat = list(shape.centroid.coords[0])
    return json.dumps([lat, lng])


def expand_region(d, config):
    expanded_d = {}
    expanded_d['id'] = 'LK-' + str(d[config['id_base_key']])
    expanded_d['name'] = d[config['name_key']]
    other_fields_key_map = config.get('other_fields_key_map')
    if other_fields_key_map:
        for k1, k2 in other_fields_key_map.items():
            expanded_d[k1] = d[k2]

    expanded_d.update(get_parent_ids_idx(expanded_d['id']))
    expanded_d['centroid'] = get_centroid(d)
    return expanded_d


def build_region(region_type):
    config = REGION_CONFIG_IDX[region_type]
    file_only = config['file_only']

    topojson_file = os.path.join(DIR_STATSL_SHAPE, file_only)
    df = geopandas.read_file(topojson_file)

    data_list = []
    for d in df.to_dict('records'):
        expanded_d = expand_region(d, config)
        data_list.append(expanded_d)
        save_geo(region_type, expanded_d['id'], d['geometry'])

    data_list = sorted(data_list, key=lambda d: d['id'])
    store_basic_data('_tmp/precensus-', region_type, data_list)


def build_precensus_ent_for_country():
    store_basic_data(
        '_tmp/precensus-',
        'country',
        [
            {
                'id': 'LK',
                'country_id': 'LK',
                'name': 'Sri Lanka',
                'population': 20_357_776,
            }
        ],
    )


def build_all_regions():
    for region_type in ["province", "district", "dsd", "gnd"]:
        build_region(region_type)


def main():
    build_precensus_ent_for_country()
    build_all_regions()


if __name__ == '__main__':
    main()

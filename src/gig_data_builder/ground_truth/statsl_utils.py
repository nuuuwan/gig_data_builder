import json
import os

import geopandas

from gig_data_builder._common import ent_types
from gig_data_builder._constants import DIR_STATSL_SHAPE
from gig_data_builder.regions import _geo

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


def get_id(d, region_type):
    config = REGION_CONFIG_IDX[region_type]
    return 'LK-' + str(d[config['id_base_key']])


def get_name(d, region_type):
    config = REGION_CONFIG_IDX[region_type]
    return d[config['name_key']]


def get_centroid(d):
    shape = d['geometry']
    lng, lat = list(shape.centroid.coords[0])
    lng, lat = _geo.normalize_point_value(lng), _geo.normalize_point_value(
        lat
    )
    return json.dumps([lat, lng])


def get_other_fields_idx(d, region_type):
    config = REGION_CONFIG_IDX[region_type]
    other_fields_key_map = config.get('other_fields_key_map')
    d2 = {}
    if other_fields_key_map:
        for k1, k2 in other_fields_key_map.items():
            d2[k1] = d[k2]
    return d2


def get_parent_ids_idx(region_id):
    n_region_id = len(region_id)
    d = {}
    for parent_type, n_parent_id in ent_types.REGION_TYPE_TO_ID_LEN.items():
        if n_region_id >= n_parent_id:
            d[parent_type + '_id'] = region_id[:n_parent_id]
    return d


def get_df(region_type):
    config = REGION_CONFIG_IDX[region_type]
    file_only = config['file_only']
    topojson_file = os.path.join(DIR_STATSL_SHAPE, file_only)
    return geopandas.read_file(topojson_file)

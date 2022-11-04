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


def add_parent_ids(d):
    region_id = d['id']
    n_region_id = len(region_id)
    for parent_type, n_parent_id in REGION_TYPE_TO_ID_LEN.items():
        if n_region_id >= n_parent_id:
            d[parent_type + '_id'] = region_id[:n_parent_id]
    return d


def expand_provinces(d):
    province_id = 'LK-%s' % d['prov_c']
    return {
        'id': province_id,
        'province_id': province_id,
        'name': d['prov_n'],
    }


def expand_districts(d):
    district_id = 'LK-%s' % d['dis_c']
    province_id = district_id[:-4]
    return {
        'id': district_id,
        'district_id': district_id,
        'province_id': province_id,
        'name': d['dis_n'],
    }


def expand_dsds(d):
    dsd_id = 'LK-%s' % d['dsd_c']
    return {
        'id': dsd_id,
        'dsd_id': dsd_id,
        'name': d['dsd_n'],
    }


def expand_gnds(d):
    gnd_id = 'LK-%s' % d['code']
    gnd_num = d['gnnum']
    return {
        'id': gnd_id,
        'gnd_id': gnd_id,
        'gnd_num': gnd_num,
        'name': d['name'],
    }


REGION_CONFIG_IDX = {
    "province": {
        'file_only': 'Provinces.json',
        'expand_regions': expand_provinces,
    },
    "district": {
        'file_only': 'Districts.json',
        'expand_regions': expand_districts,
    },
    "dsd": {
        'file_only': 'DSDivisions.json',
        'expand_regions': expand_dsds,
    },
    "gnd": {
        'file_only': 'GNDivisions.json',
        'expand_regions': expand_gnds,
    },
}


def build_region(region_type):
    config = REGION_CONFIG_IDX[region_type]
    file_only = config['file_only']
    expand_regions = config['expand_regions']

    topojson_file = os.path.join(DIR_STATSL_SHAPE, file_only)
    df = geopandas.read_file(topojson_file)

    data_list = []
    for d in df.to_dict('records'):
        expanded_d = expand_regions(d)
        expanded_d = add_parent_ids(expanded_d)
        data_list.append(expanded_d)

        shape = d['geometry']
        lng, lat = list(shape.centroid.coords[0])
        expanded_d['centroid'] = json.dumps([lat, lng])

        save_geo(region_type, expanded_d['id'], shape)

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

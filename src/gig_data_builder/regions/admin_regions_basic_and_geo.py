import json
import os

import geopandas

from gig_data_builder._basic import store_basic_data
from gig_data_builder._constants import DIR_STATSL_SHAPE
from gig_data_builder._utils import log
from gig_data_builder.regions._geo import save_geo

PREFIX = '_tmp/precensus-'


def expand_data(d):
    region_id = d['id']
    n_region_id = len(region_id)
    for parent_type, n_parent_id in [
        ['province', 4],
        ['district', 5],
        ['dsd', 7],
    ]:
        if n_region_id >= n_parent_id:
            d[parent_type + '_id'] = region_id[:n_parent_id]
    return d


def map_provinces(d):
    province_id = 'LK-%s' % d['prov_c']
    return {
        'id': province_id,
        'province_id': province_id,
        'name': d['prov_n'],
    }


def map_districts(d):
    district_id = 'LK-%s' % d['dis_c']
    province_id = district_id[:-4]
    return {
        'id': district_id,
        'district_id': district_id,
        'province_id': province_id,
        'name': d['dis_n'],
    }


def map_dsds(d):
    dsd_id = 'LK-%s' % d['dsd_c']
    return {
        'id': dsd_id,
        'dsd_id': dsd_id,
        'name': d['dsd_n'],
    }


def map_gnds(d):
    gnd_id = 'LK-%s' % d['code']
    gnd_num = d['gnnum']
    return {
        'id': gnd_id,
        'gnd_id': gnd_id,
        'gnd_num': gnd_num,
        'name': d['name'],
    }


REGION_CONFIG_LIST = [
    {
        'region_type': 'province',
        'file_only': 'Provinces.json',
        'map_regions': map_provinces,
    },
    {
        'region_type': 'district',
        'file_only': 'Districts.json',
        'map_regions': map_districts,
    },
    {
        'region_type': 'dsd',
        'file_only': 'DSDivisions.json',
        'map_regions': map_dsds,
    },
    {
        'region_type': 'gnd',
        'file_only': 'GNDivisions.json',
        'map_regions': map_gnds,
    },
]


def build_region(region_type, file_only, map_regions):
    topojson_file = os.path.join(DIR_STATSL_SHAPE, file_only)
    df = geopandas.read_file(topojson_file)

    data_list = []
    for d in df.to_dict('records'):
        new_d = expand_data(map_regions(d))
        data_list.append(new_d)

        shape = d['geometry']
        lng, lat = list(shape.centroid.coords[0])
        new_d['centroid'] = json.dumps([lat, lng])

        save_geo(region_type, new_d['id'], shape)

    data_list = sorted(data_list, key=lambda d: d['id'])
    store_basic_data(PREFIX, region_type, data_list)


def build_precensus_ent_for_country():
    store_basic_data(
        PREFIX,
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
    for config in REGION_CONFIG_LIST:
        build_region(
            config['region_type'],
            config['file_only'],
            config['map_regions'],
        )


def main():
    build_precensus_ent_for_country()
    build_all_regions()


if __name__ == '__main__':
    main()

import os

import geopandas
from utils import tsv

from gig_data_builder._constants import DIR_STATSL
from gig_data_builder._utils import log
from gig_data_builder.basic_data import get_basic_data_file
from gig_data_builder.build_init import build_dirs

# id	name	country_id	province_id	area
# population	province_capital
# fips	subs	supers	eqs	ints	centroid	centroid_altitude


def add_parent_ids(d):
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
        'func_map_regions': map_provinces,
    },
    {
        'region_type': 'district',
        'file_only': 'Districts.json',
        'func_map_regions': map_districts,
    },
    {
        'region_type': 'dsd',
        'file_only': 'DSDivisions.json',
        'func_map_regions': map_dsds,
    },
    {
        'region_type': 'gnd',
        'file_only': 'GNDivisions.json',
        'func_map_regions': map_gnds,
    },
]


def build_region(region_type, file_only, func_map_regions):
    topojson_file = os.path.join(DIR_STATSL, file_only)
    df = geopandas.read_file(topojson_file)

    data_list = sorted(
        list(
            map(
                lambda d: add_parent_ids(func_map_regions(d)),
                df.to_dict('records'),
            )
        ),
        key=lambda d: d['id'],
    )

    region_file = get_basic_data_file(region_type)
    tsv.write(region_file, data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {region_file}')


def build_all_regions():
    for config in REGION_CONFIG_LIST:
        build_region(
            config['region_type'],
            config['file_only'],
            config['func_map_regions'],
        )


if __name__ == '__main__':
    build_dirs()
    build_all_regions()

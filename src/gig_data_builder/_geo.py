import os

import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon
from utils import jsonx

from gig_data_builder._constants import DIR_DATA_GEO
from gig_data_builder._utils import log


def get_geo_dir_for_region(region_type):
    dir_data_geo_region = os.path.join(DIR_DATA_GEO, region_type)
    if not os.path.exists(dir_data_geo_region):
        os.mkdir(dir_data_geo_region)
    return dir_data_geo_region


def get_geo_file(region_type, region_id):
    return os.path.join(
        get_geo_dir_for_region(region_type), '%s.json' % region_id
    )


def get_geo(region_type, region_id):
    geo_file = get_geo_file(region_type, region_id)
    return jsonx.read(geo_file)


def get_geo_index_for_region_type(region_type):
    geo_index = {}
    for geo_file_only in os.listdir(get_geo_dir_for_region(region_type)):
        region_id = geo_file_only[:-5]
        geo_index[region_id] = get_geo(region_type, region_id)
    n_geo_index = len(geo_index.keys())
    log.info(f'Built index with {n_geo_index} items for {region_type}')
    return geo_index


def save_geo(region_type, region_id, shape, show_geo=False):
    if isinstance(shape, Polygon):
        geo_data = [list(shape.exterior.coords)]
    elif isinstance(shape, MultiPolygon):
        geo_data = list(
            map(
                lambda polygon: list(polygon.exterior.coords),
                shape,
            )
        )
    else:
        log.error('Unknown shapely shape: %s' + type(shape))
        return None

    if show_geo:
        for geo_data_item in geo_data:
            polygon = Polygon(geo_data_item)
            plt.plot(*polygon.exterior.xy)
        plt.show()

    geo_file = get_geo_file(region_type, region_id)
    jsonx.write(geo_file, geo_data)
    log.info(f'Wrote {geo_file}')

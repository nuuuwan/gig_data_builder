import json
import logging

from shapely.geometry import Polygon
from shapely.ops import unary_union

from gig_data_builder._utils import log
from gig_data_builder.regions._geo import (get_geo_index_for_region_type,
                                           save_geo)
from gig_data_builder.regions.all_region_id_map_and_lg_basic import (
    get_basic_data, get_region_id_index, store_basic_data)

logger = logging.getLogger('shapely.geos')
logger.setLevel(logging.WARNING)


def add_centroid_column(region_type, region_to_centroid):
    def add_centroid_to_row(d):
        d['centroid'] = region_to_centroid.get(d['id'])
        return d

    basic_data = get_basic_data('tmp-precensus-pregeo-', region_type)
    data_list = list(
        map(
            add_centroid_to_row,
            basic_data,
        )
    )
    store_basic_data('tmp-precensus-', region_type, data_list)


def build_geos():
    region_id_index = get_region_id_index()
    geo_index = get_geo_index_for_region_type('gnd')
    for region_type in ['ed', 'pd', 'moh', 'lg']:
        parent_to_gnds = {}
        for gnd_id, regions in region_id_index.items():
            parent_id = regions.get(region_type + '_id')
            if parent_id == '':
                continue
            if parent_id is None:
                continue
            if parent_id not in parent_to_gnds:
                parent_to_gnds[parent_id] = []
            parent_to_gnds[parent_id].append(gnd_id)

        region_to_centroid = {}
        for parent_id, gnd_ids in parent_to_gnds.items():
            gnd_geos = list(
                map(
                    lambda gnd_id: geo_index.get(gnd_id, []),
                    gnd_ids,
                )
            )

            polygon_list = list(
                map(
                    lambda gnd_geo: Polygon(gnd_geo[0]),
                    gnd_geos,
                )
            )
            valid_polygon_list = list(
                map(
                    lambda polygon: polygon
                    if polygon.is_valid
                    else polygon.buffer(0),
                    polygon_list,
                )
            )

            shape = unary_union(valid_polygon_list)
            try:
                save_geo(region_type, parent_id, shape)
                lng, lat = list(shape.centroid.coords[0])
                region_to_centroid[parent_id] = json.dumps([lat, lng])
            except BaseException:
                log.error(f'Could not build_geo for: {parent_id}')

        add_centroid_column(region_type, region_to_centroid)


if __name__ == '__main__':
    build_geos()

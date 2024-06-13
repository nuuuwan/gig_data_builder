import json
import logging
import os

from shapely.geometry import Polygon
from shapely.ops import unary_union

from gig_data_builder import _basic
from gig_data_builder._common import ent_types
from gig_data_builder._utils import log
from gig_data_builder.regions import _geo

logger = logging.getLogger('shapely.geos')
logger.setLevel(logging.WARNING)


def add_centroid_column(region_type, region_to_centroid):
    def add_centroid_to_row(d):
        d['centroid'] = region_to_centroid.get(d['id'])
        return d

    basic_data = _basic.get_basic_data(
        os.path.join('_tmp', 'precensus-pregeo-'), region_type
    )
    data_list = list(
        map(
            add_centroid_to_row,
            basic_data,
        )
    )
    _basic.store_basic_data(
        os.path.join('_tmp', 'precensus-'), region_type, data_list
    )

def fix(polygon):
    if not polygon.is_valid:
        return polygon.buffer(0)
    return polygon

def main():
    gnd_data_index = _basic.get_basic_data_index(
        os.path.join('_tmp', 'precensus-'), 'gnd'
    )
    gnd_geo_index = _geo.get_geo_index_for_region_type('gnd')
    for region_type in ent_types.NON_ADMIN_REGION_TYPES:
        parent_to_gnds = {}
        for gnd_id, gnd in gnd_data_index.items():
            parent_id = gnd.get(region_type + '_id')
            if parent_id == '':
                continue
            if parent_id is None:
                continue
            if parent_id not in parent_to_gnds:
                parent_to_gnds[parent_id] = []
            parent_to_gnds[parent_id].append(gnd_id)

        region_to_centroid = {}
        for parent_id, gnd_ids in parent_to_gnds.items():
            polygon_list = []
            for gnd_id in gnd_ids:
                gnd_geo = gnd_geo_index.get(gnd_id, [])
                for gnd_geo_item in gnd_geo:
                    polygon = fix(Polygon(gnd_geo_item))
                    polygon_list.append(polygon)

            shape = unary_union(polygon_list)
            try:
                _geo.save_geo(region_type, parent_id, shape)
                lng, lat = list(
                    map(
                        _geo.normalize_point_value,
                        list(shape.centroid.coords[0]),
                    )
                )
                region_to_centroid[parent_id] = json.dumps([lat, lng])

            except BaseException:
                log.error(f'Could not build_geo for: {parent_id}')

        n_regions = len(parent_to_gnds.keys())
        dir_geo = _geo.get_geo_dir_for_region(region_type)
        log.info(f'Wrote {n_regions} files to {dir_geo}')

        add_centroid_column(region_type, region_to_centroid)


if __name__ == '__main__':
    main()

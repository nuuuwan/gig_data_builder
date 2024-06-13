import os
import random

import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from utils import JSONFile
from _utils import log

from gig_data_builder._constants import DIR_DATA_CHECKS, DIR_DATA_GEO

random.seed(1)


def get_region_file_names(region_type):
    dir_region_type = os.path.join(DIR_DATA_GEO, region_type)
    file_list = []
    for file_only in os.listdir(dir_region_type):
        file_list.append(os.path.join(dir_region_type, file_only))
    return file_list


def save_geo_image(region_type, func_filter=None, image_file_prefix=None):
    plt.close()
    file_names = get_region_file_names(region_type)
    filtered_file_names = [
        file_name
        for file_name in file_names
        if not func_filter or func_filter(file_name)
    ]
    random.seed(0)
    random.shuffle(filtered_file_names)

    n_files = len(filtered_file_names)
    for i_file, file_name in enumerate(filtered_file_names):
        data = JSONFile(file_name).read()
        color = plt.cm.jet(i_file / n_files)
        for polygon_data in data:
            polygon = Polygon(polygon_data)
            x, y = polygon.exterior.xy
            plt.fill(x, y, color=color)

    image_file_prefix = (
        image_file_prefix if image_file_prefix else region_type
    )
    image_file = os.path.join(
        DIR_DATA_CHECKS, f'sanity_check_geos.{image_file_prefix}.png'
    )
    plt.title(image_file_prefix)
    plt.savefig(image_file)
    log.debug(f'Wrote {image_file}')
    plt.close()


def main():
    save_geo_image(
        'pd',
        lambda file_name: 'EC-01' in file_name,
        image_file_prefix="pd-Colombo",
    )
    save_geo_image(
        'pd',
        lambda file_name: 'EC-14' in file_name,
        image_file_prefix="pd-Trinco",
    )
    save_geo_image(
        'pd',
        lambda file_name: 'EC-10' in file_name,
        image_file_prefix="pd-Jaffna",
    )
    save_geo_image(
        'pd',
        lambda file_name: 'EC-11' in file_name,
        image_file_prefix="pd-Vanni",
    )
    save_geo_image(
        'gnd',
        lambda file_name: 'LK-1103' in file_name,
        image_file_prefix="gnd-Colombo-DSD",
    )

    for region_type in [
        'province',
        'ed',
        'district',
        'dsd',
        'pd',
        'lg',
        'moh',
        'gnd',
    ]:
        save_geo_image(region_type)


if __name__ == '__main__':
    main()

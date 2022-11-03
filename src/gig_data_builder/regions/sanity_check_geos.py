import os

import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from utils import JSONFile

from gig_data_builder._constants import DIR_DATA_GEO


def get_region_file_names(region_type):
    dir_region_type = os.path.join(DIR_DATA_GEO, region_type)
    file_list = []
    for file_only in os.listdir(dir_region_type):
        file_list.append(os.path.join(dir_region_type, file_only))
    return file_list


def save_geo_image(region_type):
    for file_name in get_region_file_names(region_type):
        data = JSONFile(file_name).read()
        for polygon_data in data:
            polygon = Polygon(polygon_data)
            x, y = polygon.exterior.xy
            plt.plot(x, y)

    image_file = f'sanity_check_examples/geo.{region_type}.png'
    plt.title(region_type)
    plt.savefig(image_file)
    os.system(f'open -a firefox {image_file}')
    plt.close()


if __name__ == '__main__':
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

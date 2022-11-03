import os
import random
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from utils import JSONFile, colorx

from gig_data_builder._constants import DIR_DATA_GEO
random.seed(1)

def get_region_file_names(region_type):
    dir_region_type = os.path.join(DIR_DATA_GEO, region_type)
    file_list = []
    for file_only in os.listdir(dir_region_type):
        file_list.append(os.path.join(dir_region_type, file_only))
    return file_list


def save_geo_image(region_type, func_filter=None, image_file_prefix=None):
    for file_name in get_region_file_names(region_type):
        if func_filter and not func_filter(file_name):
            continue

        color = colorx.random_hex()
        data = JSONFile(file_name).read()
        for polygon_data in data:
            polygon = Polygon(polygon_data)
            x, y = polygon.exterior.xy
            plt.fill(x, y, color=color)


    image_file_prefix = image_file_prefix if image_file_prefix else region_type
    image_file = f'sanity_check_examples/geo.{image_file_prefix}.png'
    plt.title(image_file_prefix)
    plt.savefig(image_file)
    os.system(f'open -a firefox {image_file}')
    plt.close()


if __name__ == '__main__':
    save_geo_image('pd', lambda file_name: 'EC-01' in file_name,image_file_prefix="pd-Colombo")
    save_geo_image('pd', lambda file_name: 'EC-14' in file_name,image_file_prefix="pd-Trinco")
    save_geo_image('pd', lambda file_name: 'EC-10' in file_name,image_file_prefix="pd-Jaffna")
    save_geo_image('pd', lambda file_name: 'EC-11' in file_name,image_file_prefix="pd-Vanni")
    save_geo_image('gnd', lambda file_name: 'LK-1103' in file_name,image_file_prefix="gnd-Colombo-DSD")

    
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

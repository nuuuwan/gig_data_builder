import os
DIR_STATSL = 'src/gig_data_builder/raw_data/statslmap-selection/app/shape'

def build_provinces():
    topojson_file = os.path.join(
        DIR_STATSL,
        'Provinces.json',
    )


if __name__ == '__main__':
    build_provinces()

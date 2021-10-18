import os

from gig_data_builder._constants import DIR_DATA, DIR_DATA_CENSUS, DIR_DATA_GEO


def build_dirs():
    os.system(f'rm -rf {DIR_DATA}')
    os.mkdir(DIR_DATA)
    os.mkdir(DIR_DATA_GEO)
    os.mkdir(DIR_DATA_CENSUS)

if __name__ == '__main__':
    build_dirs()

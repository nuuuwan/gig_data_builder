import os

from gig_data_builder._constants import DIR_DATA, DIR_DATA_CENSUS, DIR_DATA_GEO


def __build_dirs__():
    for dir in [DIR_DATA, DIR_DATA_GEO, DIR_DATA_CENSUS]:
        os.system(f'rm -rf {dir}')
        os.mkdir(dir)


if __name__ == '__main__':
    __build_dirs__()

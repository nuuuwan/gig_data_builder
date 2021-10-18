import os

from gig_data_builder._constants import DIR_DATA, DIR_DATA_CENSUS, DIR_DATA_GEO


def __build_dirs__():
    os.system(f'rm -rf {DIR_DATA}/*')
    for dir in [DIR_DATA_GEO, DIR_DATA_CENSUS]:
        os.mkdir(dir)


if __name__ == '__main__':
    __build_dirs__()

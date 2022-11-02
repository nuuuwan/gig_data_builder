import os

from gig_data_builder._constants import (DIR_DATA_CENSUS, DIR_DATA_ELECTIONS,
                                         DIR_DATA_GEO)


def __build_dirs__():
    for dir in [DIR_DATA_GEO, DIR_DATA_CENSUS, DIR_DATA_ELECTIONS]:
        if not os.path.exists(dir):
            os.mkdir(dir)


if __name__ == '__main__':
    __build_dirs__()

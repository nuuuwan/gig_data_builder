import os

from gig_data_builder._constants import DIR_DATA, DIR_DATA_GEO


def build_dirs():
    if not os.path.exists(DIR_DATA):
        os.mkdir(DIR_DATA)
        os.mkdir(DIR_DATA_GEO)

import os

from gig_data_builder._constants import DIR_DATA


def build_dirs():
    if not os.path.exists(DIR_DATA):
        os.mkdir(DIR_DATA)

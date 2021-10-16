import os

from utils import tsv

from gig_data_builder._constants import DIR_DATA


def get_basic_data_file(region_type):
    return os.path.join(DIR_DATA, f'{region_type}.basic.tsv')


def get_basic_data(region_type):
    basic_data_file = get_basic_data_file(region_type)
    return tsv.read(basic_data_file)

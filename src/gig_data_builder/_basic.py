import os

from utils import TSVFile

from gig_data_builder._constants import DIR_DATA
from gig_data_builder._utils import log


def get_basic_data_file(prefix, region_type):
    return os.path.join(DIR_DATA, f'{prefix}{region_type}.tsv')


def get_basic_data(prefix, region_type):
    basic_data_file = get_basic_data_file(prefix, region_type)
    if not os.path.exists(basic_data_file):
        log.error(f'File not found: {basic_data_file}')
        return None
    return TSVFile(basic_data_file).read()


def get_basic_data_index(prefix, region_type):
    data_list = get_basic_data(prefix, region_type)
    return dict(
        zip(
            list(map(lambda d: d['id'], data_list)),
            data_list,
        )
    )


def store_basic_data(prefix, region_type, data_list):
    basic_data_file = get_basic_data_file(prefix, region_type)
    TSVFile(basic_data_file).write(data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {basic_data_file}')

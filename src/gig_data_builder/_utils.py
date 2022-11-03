"""Utils."""

from utils import logx, tsv

log = logx.get_logger('gig_data_builder')


def get_data_list(file_name):
    return tsv.read(file_name)


def get_data_index(file_name):
    data_list = get_data_list(file_name)
    return dict(
        zip(
            list(map(lambda d: d['entity_id'], data_list)),
            data_list,
        )
    )

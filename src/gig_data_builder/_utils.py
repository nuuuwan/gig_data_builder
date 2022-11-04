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


def dedupe(d_list, func_key):
    return list(
        dict(
            list(
                map(
                    lambda d: [func_key(d), d],
                    d_list,
                )
            )
        ).values(),
    )

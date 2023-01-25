"""Utils."""

from utils import Log, TSVFile

log = Log('gig_data_builder')


def get_data_list(file_name):
    return TSVFile(file_name).read()


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


def parse_float(x):
    try:
        return (float)(x)
    except BaseException:
        return 0


def parse_int(x):
    return (int)(parse_float(x))

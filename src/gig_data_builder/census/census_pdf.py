import os

from utils import TSVFile

from gig_data_builder import _basic
from gig_data_builder._constants import DIR_DATA_GIG2
from gig_data_builder._utils import log

TABLE_SHORT_NAME_LIST = ['economy-economic-activity', 'education-educational-attainment']


def get_table_file_name(table_short_name):
    m = table_short_name
    e = 'regions'
    t = '2012'
    file_name_only = f'{m}.{e}.{t}.tsv'
    return os.path.join(DIR_DATA_GIG2, file_name_only)


def parse_int(x):
    try:
        return (int)(x)
    except BaseException:
        return 0


def map_table_row(d):
    new_d = {}
    for k, v in d.items():
        if k in [
            'entity_id',
            'region_type',
            'total',
            'region_name',
            'i_row',
            'gnd_num',
        ]:
            continue
        new_d[k] = parse_int(v)
    return {'entity_id': d['region_id']} | new_d


def get_table_data_list(table_short_name):
    tsv_file = f'data_ground_truth/census/{table_short_name}.expanded.tsv'
    d_list = TSVFile(tsv_file).read()
    table_data_list = list(
        map(
            map_table_row,
            list(
                filter(
                    lambda d: d['region_type'] == 'gnd',
                    d_list,
                )
            ),
        )
    )
    return table_data_list


def expand_parents(table_data_list):
    gnd_data_index = _basic.get_basic_data_index('_tmp/precensus-', 'gnd')

    parent_to_k_to_v = {}
    for d in table_data_list:
        gnd_id = d['entity_id']
        gnd = gnd_data_index.get(gnd_id)
        if gnd is None:
            log.error(f'No region info for gnd: {gnd_id}')
            continue

        for region_type in [
            'country',
            'province',
            'district',
            'dsd',
            'ed',
            'pd',
            'lg',
            'moh',
        ]:
            if region_type == 'country':
                parent_id = 'LK'
            else:
                parent_id = gnd.get(region_type + '_id', None)
                if parent_id is None or parent_id == '':
                    continue

            if parent_id not in parent_to_k_to_v:
                parent_to_k_to_v[parent_id] = {}
            for k, v in d.items():
                if k == 'entity_id':
                    continue
                if k not in parent_to_k_to_v[parent_id]:
                    parent_to_k_to_v[parent_id][k] = 0
                parent_to_k_to_v[parent_id][k] += v

    for parent_id, k_to_v in parent_to_k_to_v.items():
        table_data_list.append({**{'entity_id': parent_id}, **k_to_v})
    return table_data_list


def build_table(table_short_name):
    table_data_list = get_table_data_list(table_short_name)
    table_data_list = expand_parents(table_data_list)
    table_data_list = sorted(table_data_list, key=lambda d: d['entity_id'])
    n = len(table_data_list)

    table_file_name = get_table_file_name(table_short_name)
    TSVFile(table_file_name).write(table_data_list)
    log.debug(f'Writing {n} rows to {table_file_name}')


def main():
    for table_short_name in TABLE_SHORT_NAME_LIST:
        build_table(table_short_name)


if __name__ == '__main__':
    main()

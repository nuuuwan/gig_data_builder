import os

from gig_data_builder._basic import (get_basic_data, get_data_index,
                                     store_basic_data)
from gig_data_builder._constants import DIR_DATA_GIG2
from gig_data_builder._utils import log


def expand_all():
    population_index = get_data_index(
        os.path.join(DIR_DATA_GIG2, 'population-total.regions.2012.tsv')
    )

    def expand_row(d):
        if 'id' in d:
            id = d['id']
        elif 'gnd_id' in d:
            id = d['gnd_id']
        else:
            log.error('Invalid row format!')
        d['population'] = population_index.get(id, {}).get('total_population')
        return d

    for region_type in [
        'country',
        'province',
        'district',
        'dsd',
        'gnd',
        'ed',
        'pd',
        'moh',
        'lg',
        'region_id_map',
    ]:
        data_list = list(
            map(
                expand_row,
                get_basic_data('_tmp/precensus-', region_type),
            )
        )
        store_basic_data('ents/', region_type, data_list)
        log.info(f'Expanded {region_type}')


if __name__ == '__main__':
    expand_all()

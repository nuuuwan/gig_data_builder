from gig_data_builder._basic import get_basic_data, store_basic_data
from gig_data_builder._utils import log
from gig_data_builder.census.census import get_census_data_index


def expand_all():
    population_index = get_census_data_index('total_population')

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
        store_basic_data('', region_type, data_list)
        log.info(f'Expanded {region_type}')


if __name__ == '__main__':
    expand_all()

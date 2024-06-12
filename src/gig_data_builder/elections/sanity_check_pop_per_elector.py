import os

from utils_future import TSVFile

from gig_data_builder._basic import get_basic_data_index
from gig_data_builder._constants import DIR_DATA_CHECKS, DIR_DATA_GIG2
from gig_data_builder._utils import get_data_index, log


def main():
    election_2020_index = os.path.join(
        DIR_DATA_GIG2,
        'government-elections-parliamentary.regions-ec.2020.tsv',
    )

    pd_index = get_basic_data_index(os.path.join('ents', ''), 'pd')
    election_index = get_data_index(election_2020_index)

    sanity_data_list = []
    for pd_id, pd in pd_index.items():
        pd_name = pd['name']
        pop_2012 = (float)(pd['population'])
        electors_2020 = (float)(election_index[pd_id]['electors'])
        pop_per_elector = pop_2012 / electors_2020
        sanity_data_list.append(
            dict(
                pd_id=pd_id,
                pd_name=pd_name,
                pop_2012=pop_2012,
                electors_2020=electors_2020,
                pop_per_elector=pop_per_elector,
            )
        )
    sanity_data_list = sorted(
        sanity_data_list,
        key=lambda d: d['pop_per_elector'],
    )
    sanity_file = os.path.join(
        DIR_DATA_CHECKS, 'sanity_check_pop_per_elector.tsv'
    )
    TSVFile(sanity_file).write(sanity_data_list)
    log.info(f'Saved {sanity_file}')


if __name__ == '__main__':
    main()

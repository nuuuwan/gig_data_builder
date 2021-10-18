import os

from utils import jsonx, www

from gig_data_builder._constants import DIR_ELECTIONS_RESULTS
from gig_data_builder._utils import log

SUMMARY_STAT_KEYS = ['valid', 'rejected', 'polled', 'electors']
ELECTION_CONFIGS = {
    'presidential': {
        'dir_remote': os.path.join(
            'https://raw.githubusercontent.com',
            'nuuuwan/elections_lk/data',
        ),
        'func_get_file': lambda year: f'elections_lk.presidential.{year}.json',
        'year_list': [1982, 1988, 1994, 1999, 2005, 2010, 2015, 2019],
        'field_key_votes': 'votes',
    },
    'parliamentary': {
        'dir_remote': os.path.join(
            'https://raw.githubusercontent.com',
            'nuuuwan/gen_elec_sl/master/elections_lk_react',
            'public/data/elections',
        ),
        'func_get_file': lambda year: f'gen_elec_sl.ec.results.{year}.json',
        'year_list': [1989, 1994, 2000, 2001, 2004, 2010, 2015, 2020],
        'field_key_votes': 'vote_count',
    },
}


def reverse_download():
    for election_type, config in ELECTION_CONFIGS.items():
        dir_remote = config['dir_remote']
        func_get_file = config['func_get_file']
        config['field_key_votes']
        for year in config['year_list']:
            remote_url = os.path.join(
                dir_remote,
                func_get_file(year),
            )
            data = www.read_json(remote_url)
            data_file = os.path.join(
                DIR_ELECTIONS_RESULTS,
                f'{election_type}_election_{year}.json',
            )
            jsonx.write(data_file, data)
            log.info(
                f'Downloaded from {remote_url} to {data_file}'
            )

if __name__ == '__main__':
    reverse_download()

import os

from gig_data_builder._basic import get_basic_data_file
from gig_data_builder._constants import DIR_ELECTIONS
from gig_data_builder._utils import log

PREFIX = 'tmp-precensus-pregeo-'

if __name__ == '__main__':
    pd_basic_file = get_basic_data_file(PREFIX, 'pd')
    os.system(f'cp {DIR_ELECTIONS}/pd.basic.tsv {pd_basic_file}')
    log.info(f'Wrote {pd_basic_file}')

    ed_basic_file = get_basic_data_file(PREFIX, 'ed')
    os.system(f'cp {DIR_ELECTIONS}/ed.basic.tsv {ed_basic_file}')
    log.info(f'Wrote {ed_basic_file}')

import os

from gig_data_builder._constants import DIR_ELECTIONS
from gig_data_builder.basic_data import get_basic_data_file

if __name__ == '__main__':
    pd_basic_file = get_basic_data_file('pd')
    os.system(f'cp {DIR_ELECTIONS}/pd.basic.tsv {pd_basic_file}')
    ed_basic_file = get_basic_data_file('ed')
    os.system(f'cp {DIR_ELECTIONS}/ed.basic.tsv {ed_basic_file}')

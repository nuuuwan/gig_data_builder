import os
import shutil

from gig_data_builder._basic import get_basic_data_file
from gig_data_builder._common import ent_types
from gig_data_builder._constants import DIR_ELECTIONS
from gig_data_builder._utils import log

PREFIX = os.path.join('_tmp', 'precensus-pregeo-')


def build_precensus_pregeo_ent_for_election_regions(region_type):
    basic_file = get_basic_data_file(PREFIX, region_type)
    shutil.copyfile(
        os.path.join(DIR_ELECTIONS, f'{region_type}.basic.tsv'), basic_file
    )
    log.info(f'Wrote {basic_file}')


def main():
    for region_type in ent_types.ELECTION_REGION_TYPES:
        build_precensus_pregeo_ent_for_election_regions(region_type)


if __name__ == '__main__':
    main()

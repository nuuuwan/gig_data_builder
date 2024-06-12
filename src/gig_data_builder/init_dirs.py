import os
import shutil

from gig_data_builder._constants import (DIR_DATA_CHECKS, DIR_DATA_ENTS,
                                         DIR_DATA_GEO, DIR_DATA_GIG2,
                                         DIR_DATA_TMP)
from gig_data_builder._utils import log


def main():
    for dir in [
        DIR_DATA_TMP,
        DIR_DATA_ENTS,
        DIR_DATA_GEO,
        DIR_DATA_GIG2,
        DIR_DATA_CHECKS,
    ]:
        shutil.rmtree(dir, ignore_errors=True)
        os.makedirs(dir)
        log.info(f'(Re)Created {dir}')


if __name__ == '__main__':
    main()

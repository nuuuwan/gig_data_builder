"""Constants."""
import os

CACHE_NAME = 'gig_data_builder'
CACHE_TIMEOUT = 3600

DIR_DATA = '/tmp/gig_data_builder'

DIR_RAW_DATA = 'src/gig_data_builder/raw_data'
DIR_STATSL = os.path.join(DIR_RAW_DATA, 'statslmap-selection/app/shape')
DIR_REGION_ID_MAP = os.path.join(DIR_RAW_DATA, 'region_id_map')

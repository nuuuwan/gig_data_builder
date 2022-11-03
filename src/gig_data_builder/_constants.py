"""Constants."""
import os

CACHE_NAME = 'gig_data_builder'
CACHE_TIMEOUT = 3600

DIR_DATA = '/Users/nuwan.senaratna/Not.Dropbox/_CODING/data/gig-data'
DIR_TMP_DATA = '/tmp'

DIR_DATA_GEO = os.path.join(
    DIR_DATA,
    'geo',
)
DIR_DATA_CENSUS = os.path.join(DIR_DATA, 'census')
DIR_DATA_ELECTIONS = os.path.join(DIR_DATA, 'elections')

DIR_RAW_DATA = 'src/gig_data_builder/data_ground_truth'
DIR_STATSL = os.path.join(DIR_RAW_DATA, 'statslmap_selection')
DIR_STATSL_SHAPE = os.path.join(DIR_STATSL, 'app/shape')
DIR_STATSL_DATA = os.path.join(DIR_STATSL, 'app/data')

DIR_REGION_ID_MAP = os.path.join(DIR_RAW_DATA, 'region_id_map')
DIR_ELECTIONS = os.path.join(DIR_RAW_DATA, 'elections')
DIR_MOH = os.path.join(DIR_RAW_DATA, 'moh')

DIR_ELECTIONS_RESULTS = os.path.join(DIR_RAW_DATA, 'elections_results')

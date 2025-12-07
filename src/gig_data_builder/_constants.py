"""Constants."""

import os
import sys
import tempfile

from gig_data_builder._utils import log

CACHE_NAME = "gig_data_builder"
CACHE_TIMEOUT = 3600

DIR_TMP = tempfile.gettempdir()
log.debug(f"{DIR_TMP=}")
if "GIG_DATA_BUILDER_DIR_DATA" not in os.environ:
    for line in [
        "❌ GIG_DATA_BUILDER_DIR_DATA does not exist",
        "cd <path>",
        "git clone https://github.com/nuuuwan/gig-data.git",
        "GIG_DATA_BUILDER_DIR_DATA=<path>",
        "export GIG_DATA_BUILDER_DIR_DATA",
    ]:
        log.error(line)
    sys.exit(1)

DIR_DATA = os.environ["GIG_DATA_BUILDER_DIR_DATA"]
log.debug(f"{DIR_DATA=}")


DIR_DATA_TMP = os.path.join(DIR_DATA, "_tmp")
DIR_DATA_GEO = os.path.join(
    DIR_DATA,
    "geo",
)
DIR_DATA_CHECKS = os.path.join(DIR_DATA, "_checks")
DIR_DATA_GIG2 = os.path.join(DIR_DATA, "gig2")
DIR_DATA_CENSUS = os.path.join(DIR_DATA, "census")
DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")


DIR_GROUND_TRUTH_DATA = "data_ground_truth"
DIR_STATSL = os.path.join(DIR_GROUND_TRUTH_DATA, "statslmap_selection")
DIR_STATSL_SHAPE = os.path.join(DIR_STATSL, "app", "shape")
DIR_STATSL_DATA = os.path.join(DIR_STATSL, "app", "data")

DIR_REGION_ID_MAP = os.path.join(DIR_GROUND_TRUTH_DATA, "region_id_map")
DIR_ELECTIONS = os.path.join(DIR_GROUND_TRUTH_DATA, "elections")
DIR_MOH = os.path.join(DIR_GROUND_TRUTH_DATA, "moh")

DIR_ELECTIONS_RESULTS = os.path.join(
    DIR_GROUND_TRUTH_DATA, "elections_results"
)

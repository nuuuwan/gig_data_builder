import os

from utils import JSONFile

from gig_data_builder import _basic
from gig_data_builder._utils import log
from gig_data_builder.ground_truth import pd_utils


def get_missing_gnd_id_to_pd_id():
    json_file_path = os.path.join("_variables", "missing_gnd_id_to_pd_id.json")
    return JSONFile(json_file_path).read()


def add_pd_to_gnd(gnd_to_pd):
    missing_gnd_id_to_pd_id = get_missing_gnd_id_to_pd_id()
    gnd_data_list = _basic.get_basic_data(
        os.path.join("_tmp", "precensus-"), "gnd"
    )
    gnd_data_list2 = []
    n = len(gnd_data_list)
    n_missing = 0
    for d in gnd_data_list:
        gnd_id = d["gnd_id"]
        pd_id = gnd_to_pd.get(gnd_id, None)
        if not pd_id:
            pd_id = missing_gnd_id_to_pd_id.get(gnd_id, None)

        if not pd_id:
            n_missing += 1

        d["pd_id"] = pd_id
        gnd_data_list2.append(d)
    _basic.store_basic_data(
        os.path.join("_tmp", "precensus-"), "gnd", gnd_data_list2
    )
    if n_missing > 0:
        log.warning(f"No PD for {n_missing}/{n} GNDs")


def main():
    gnd_to_pd = pd_utils.get_gnd_to_pd()
    add_pd_to_gnd(gnd_to_pd)


if __name__ == "__main__":
    main()

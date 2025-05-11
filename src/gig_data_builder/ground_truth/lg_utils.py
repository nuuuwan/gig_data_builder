import os

from utils import JSONFile


def get_lg_id_to_name_and_gnd_to_lg():
    lg_id_to_lg_info = JSONFile(
        os.path.join("data_ground_truth", "lg", "lg_id_to_lg_info.json")
    ).read()
    gnd_to_lg = JSONFile(
        os.path.join("data_ground_truth", "lg", "gnd_id_to_lg_id.json")
    ).read()

    return (lg_id_to_lg_info, gnd_to_lg)

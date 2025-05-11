import os

from gig_data_builder import _basic
from gig_data_builder.ground_truth import lg_utils


def build_precensus_pregeo_lg(lg_id_to_lg_info):
    lg_data_list = []
    for lg_id, lg_info in sorted(
        lg_id_to_lg_info.items(),
        key=lambda x: x[0],
    ):
        district_id = lg_info["district_id"]
        province_id = district_id[:4]
        d = {
            "id": lg_id,
            "lg_id": lg_id,
            "name": lg_info["lg_name"],
            "code": lg_info["lg_code"],
            "province_id": province_id,
            "district_id": district_id,
            "_LEGACY_old_lg_id": lg_info["old_lg_id"],
        }
        lg_data_list.append(d)
    _basic.store_basic_data(
        os.path.join("_tmp", "precensus-pregeo-"), "lg", lg_data_list
    )


def main():
    [lg_id_to_lg_info, _] = lg_utils.get_lg_id_to_name_and_gnd_to_lg()
    build_precensus_pregeo_lg(lg_id_to_lg_info)


if __name__ == "__main__":
    main()

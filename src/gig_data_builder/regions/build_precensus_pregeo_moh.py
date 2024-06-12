from gig_data_builder import _basic
from gig_data_builder.ground_truth import moh_utils
import os

def build_precensus_pregeo_moh(moh_id_to_name, moh_to_district):
    district_data_index = _basic.get_basic_data_index(
        os.path.join('_tmp', 'precensus-'), 'district'
    )
    moh_data_list = []
    for moh_id, moh_name in moh_id_to_name.items():
        district_id = moh_to_district[moh_id]
        district = district_data_index[district_id]
        d = {
            'id': moh_id,
            'moh_id': moh_id,
            'name': moh_name,
            'province_id': district['province_id'],
            'district_id': district_id,
            'ed_id': district['ed_id'],
        }
        moh_data_list.append(d)
    _basic.store_basic_data(os.path.join('_tmp', 'precensus-pregeo-'), 'moh', moh_data_list)


def main():
    [
        moh_id_to_name,
        _,
        moh_to_district,
    ] = moh_utils.get_moh_id_to_name_and_gnd_to_moh_and_moh_to_district()
    build_precensus_pregeo_moh(moh_id_to_name, moh_to_district)


if __name__ == '__main__':
    main()

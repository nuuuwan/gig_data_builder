from gig_data_builder import _basic
from gig_data_builder.ground_truth import lg_utils
import os

def build_precensus_pregeo_lg(lg_id_to_name):
    lg_data_list = []
    for lg_id, lg_name in sorted(
        lg_id_to_name.items(),
        key=lambda x: x[0],
    ):
        district_id_num = lg_id[3:5]
        district_id = f'LK-{district_id_num}'
        province_id = district_id[:4]
        d = {
            'id': lg_id,
            'lg_id': lg_id,
            'name': lg_name,
            'province_id': province_id,
            'district_id': district_id,
        }
        lg_data_list.append(d)
    _basic.store_basic_data(os.path.join('_tmp', 'precensus-pregeo-'), 'lg', lg_data_list)


def main():
    [lg_id_to_name, _] = lg_utils.get_lg_id_to_name_and_gnd_to_lg()
    build_precensus_pregeo_lg(lg_id_to_name)


if __name__ == '__main__':
    main()

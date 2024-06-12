from gig_data_builder import _basic
from gig_data_builder._utils import log
from gig_data_builder.ground_truth import moh_utils


def add_moh_to_gnd(gnd_to_moh):
    gnd_data_list = _basic.get_basic_data(
        os.path.join('_tmp', 'premoh-prelg-precensus-'), 'gnd'
    )
    gnd_data_list2 = []
    n = len(gnd_data_list)
    n_missing = 0
    for d in gnd_data_list:
        moh_id = gnd_to_moh.get(d['gnd_id'], None)
        if not moh_id:
            n_missing += 1
        d['moh_id'] = moh_id
        gnd_data_list2.append(d)
    _basic.store_basic_data(os.path.join('_tmp', 'prelg-precensus-'), 'gnd', gnd_data_list2)
    log.warning(f'No MOH for {n_missing}/{n} GNDs')


def main():
    [
        _,
        gnd_to_moh,
        _,
    ] = moh_utils.get_moh_id_to_name_and_gnd_to_moh_and_moh_to_district()
    add_moh_to_gnd(gnd_to_moh)


if __name__ == '__main__':
    main()

from gig_data_builder import _basic
from gig_data_builder._utils import log
from gig_data_builder.ground_truth import lg_utils


def add_lg_to_gnd(gnd_to_lg):
    gnd_data_list = _basic.get_basic_data('_tmp/prelg-precensus-', 'gnd')
    gnd_data_list2 = []
    n = len(gnd_data_list)
    n_missing = 0
    for d in gnd_data_list:
        lg_id = gnd_to_lg.get(d['gnd_id'], None)
        if not lg_id:
            n_missing += 1
        d['lg_id'] = lg_id
        gnd_data_list2.append(d)
    _basic.store_basic_data('_tmp/precensus-', 'gnd', gnd_data_list2)
    log.warning(f'No LG for {n_missing}/{n} GNDs')


def main():
    [_, gnd_to_lg] = lg_utils.get_lg_id_to_name_and_gnd_to_lg()
    add_lg_to_gnd(gnd_to_lg)


if __name__ == '__main__':
    main()

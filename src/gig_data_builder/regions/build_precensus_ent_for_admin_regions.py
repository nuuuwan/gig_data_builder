from gig_data_builder._basic import store_basic_data
from gig_data_builder._common import ent_types
from gig_data_builder.ground_truth import statsl_utils


def expand_region(d, region_type):
    expanded_d = {}
    expanded_d['id'] = statsl_utils.get_id(d, region_type)
    expanded_d['name'] = statsl_utils.get_name(d, region_type)
    expanded_d['centroid'] = statsl_utils.get_centroid(d)
    expanded_d.update(statsl_utils.get_other_fields_idx(d, region_type))
    expanded_d.update(statsl_utils.get_parent_ids_idx(expanded_d['id']))
    return expanded_d


def build_precensus_ent_for_admin_regions(region_type):
    df = statsl_utils.get_df(region_type)

    data_list = sorted(
        list(
            map(
                lambda d: expand_region(d, region_type),
                df.to_dict('records'),
            )
        ),
        key=lambda d: d['id'],
    )

    store_basic_data('_tmp/precensus-', region_type, data_list)


def main():
    for region_type in ent_types.ADMIN_REGION_TYPES:
        build_precensus_ent_for_admin_regions(region_type)


if __name__ == '__main__':
    main()

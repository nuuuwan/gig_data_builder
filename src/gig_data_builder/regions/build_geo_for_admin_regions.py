from gig_data_builder._common import ent_types
from gig_data_builder._utils import log
from gig_data_builder.ground_truth import statsl_utils
from gig_data_builder.regions._geo import save_geo


def build_geo_for_admin_regions(region_type):
    df = statsl_utils.get_df(region_type)

    for d in df.to_dict('records'):
        id = statsl_utils.get_id(d, region_type)
        save_geo(region_type, id, d['geometry'])
    log.info(f'Saved geos for {region_type}')


def main():
    for region_type in ent_types.ADMIN_REGION_TYPES:
        build_geo_for_admin_regions(region_type)


if __name__ == '__main__':
    main()

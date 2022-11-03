import init_dirs
from census import census, expand_regions_with_census_info
from elections import elections_results, sanity_check_pop_per_elector
from regions import (admin_regions_basic_and_geo,
                     all_region_id_map_and_lg_basic, elections_basic,
                     moh_basic_and_region_id_map, non_admin_region_geo,
                     sanity_check_geos)


def print_line():
    print('-' * 64)


def print_title(text):
    print_line()
    print(text)
    print_line()


def main():
    print_title("initialize dirs")
    init_dirs.main()

    print_title("_tmp/precensus-[country|province|dsd|gnd].tsv")
    admin_regions_basic_and_geo.main()

    print_title("_tmp/precensus-pregeo-[ed|pd].tsv")
    elections_basic.main()

    print_title("_tmp/precensus-pregeo-moh.tsv")
    moh_basic_and_region_id_map.main()

    print_title(
        "_tmp/precensus-pregeo-lg.tsv _tmp/precensus-region_id_map.tsv"
    )
    all_region_id_map_and_lg_basic.main()

    print_title("_tmp/precensus-[ed|pd|moh|lg].tsv")
    non_admin_region_geo.main()

    print_title("census/data.*.tsv")
    census.main()

    print_title("[country|province|dsd|gnd|ed|pd|moh|lg].tsv")
    expand_regions_with_census_info.main()

    print_title(
        "gig2/government-elections-[presidential|parliamentary]"
        + ".regions-ec.{year}.tsv"
    )
    elections_results.main()

    print_title("sanity checks")
    sanity_check_pop_per_elector.main()
    sanity_check_geos.main()


if __name__ == '__main__':
    main()

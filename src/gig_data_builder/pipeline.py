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
_ = print_title

def main():
    _("initialize dirs")
    init_dirs.main()

    _("_tmp/precensus-[country|province|dsd|gnd].tsv")
    admin_regions_basic_and_geo.main()

    _("_tmp/precensus-pregeo-[ed|pd].tsv")
    elections_basic.main()

    _("_tmp/precensus-pregeo-moh.tsv")
    moh_basic_and_region_id_map.main()

    _(
        "_tmp/precensus-pregeo-lg.tsv _tmp/precensus-region_id_map.tsv"
    )
    all_region_id_map_and_lg_basic.main()

    _("_tmp/precensus-[ed|pd|moh|lg].tsv")
    non_admin_region_geo.main()

    _("census/data.*.tsv")
    census.main()

    _("[country|province|dsd|gnd|ed|pd|moh|lg].tsv")
    expand_regions_with_census_info.main()

    _(
        "gig2/government-elections-[presidential|parliamentary]"
        + ".regions-ec.{year}.tsv"
    )
    elections_results.main()

    _("sanity checks")
    sanity_check_pop_per_elector.main()
    sanity_check_geos.main()


if __name__ == '__main__':
    main()

import init_dirs
from census import add_census_info_to_regions, census, census_pdf
from elections import elections_results, sanity_check_pop_per_elector
from regions import (add_lg_to_gnd, add_moh_to_gnd, add_pd_to_gnd,
                     build_geo_for_admin_regions,
                     build_geo_for_nonadmin_regions,
                     build_precensus_ent_for_admin_regions,
                     build_precensus_ent_for_country,
                     build_precensus_pregeo_ent_for_election_regions,
                     build_precensus_pregeo_lg, build_precensus_pregeo_moh,
                     sanity_check_geos)

TEST_MODE = False


def print_line():
    print('-' * 64)


def print_title(text):
    print_line()
    print(text)
    print_line()


_ = print_title


def testMain():
    assert TEST_MODE

    _("_tmp/precensus-pregeo-moh.tsv")
    build_precensus_pregeo_moh.main()

    _("_tmp/prelg-precensus-gnd.tsv")
    add_moh_to_gnd.main()


def main():
    _("initialize dirs")
    init_dirs.main()

    _("_tmp/precensus-country.tsv")
    build_precensus_ent_for_country.main()
    _(
        "_tmp/precensus-[province|district|dsd].tsv"
        + " _tmp/premoh-prelg-precensus-gnd.tsv"
    )
    build_precensus_ent_for_admin_regions.main()
    _("geo/[country|province|dsd|gnd]/*.json")
    build_geo_for_admin_regions.main()

    _("_tmp/precensus-pregeo-[ed|pd].tsv")
    build_precensus_pregeo_ent_for_election_regions.main()

    _("_tmp/precensus-pregeo-moh.tsv")
    build_precensus_pregeo_moh.main()

    _("_tmp/prelg-precensus-gnd.tsv")
    add_moh_to_gnd.main()

    _("_tmp/precensus-pregeo-lg.tsv")
    build_precensus_pregeo_lg.main()

    _("_tmp/precensus-gnd.tsv")
    add_lg_to_gnd.main()

    _("_tmp/precensus-gnd.tsv")
    add_pd_to_gnd.main()

    _("_tmp/precensus-[ed|pd|moh|lg].tsv")
    build_geo_for_nonadmin_regions.main()
    sanity_check_geos.main()

    _("census/data.*.tsv")
    census.main()
    census_pdf.main()

    _("[country|province|dsd|gnd|ed|pd|moh|lg].tsv")
    add_census_info_to_regions.main()

    _(
        "gig2/government-elections-[presidential|parliamentary]"
        + ".regions-ec.{year}.tsv"
    )
    elections_results.main()
    sanity_check_pop_per_elector.main()


if __name__ == '__main__':
    if TEST_MODE:
        testMain()
    else:
        main()

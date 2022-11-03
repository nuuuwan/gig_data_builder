function run { python3 src/gig_data_builder/$1; }
function echo_line { echo "--------------------------------"; }
function comment { echo_line; echo "$1" ; echo_line; }

comment before
run init_dirs.py

comment "tmp-precensus-[country|province|dsd|gnd].tsv"
run regions/admin_regions_basic_and_geo.py

comment "tmp-precensus-pregeo-[ed|pd].tsv"
run regions/elections_basic.py

comment "tmp-precensus-pregeo-moh.tsv"
run regions/moh_basic_and_region_id_map.py

comment "tmp-precensus-pregeo-lg.tsv, tmp-precensus-region_id_map.tsv"
run regions/all_region_id_map_and_lg_basic.py

comment "tmp-precensus-[ed|pd|moh|lg].tsv"
run regions/non_admin_region_geo.py

comment "census/data.*.tsv etc."
run census/census.py

comment "[country|province|dsd|gnd|ed|pd|moh|lg].tsv"
run census-regions/expand_regions_with_census_info.py

comment "elections/parliamentary_election_*.tsv, elections/presidential_election_*.tsv"
run elections/elections_results.py

echo '----------------------------------------------------------------'
ls /Users/nuwan.senaratna/Not.Dropbox/_CODING/data/gig-data

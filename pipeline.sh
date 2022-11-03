function run { python3 src/gig_data_builder/$1; }

# tmp-precensus-[country|province|dsd|gnd].tsv
run regions/admin_regions_basic_and_geo.py

# tmp-precensus-pregeo-[ed|pd].tsv
run elections/elections_basic.py

# tmp-precensus-pregeo-moh.tsv
run regions/moh_basic_and_region_id_map.py

# tmp-precensus-pregeo-lg.tsv, tmp-precensus-region_id_map.tsv
run regions/all_region_id_map_and_lg_basic.py

# tmp-precensus-[ed|pd|moh|lg].tsv
run regions/non_admin_region_geo.py

# census/data.*.tsv etc.
run census/census.py

# [country|province|dsd|gnd|ed|pd|moh|lg].tsv
run census-regions/expand_regions_with_census_info.py

# elections/parliamentary_election_*.tsv, elections/presidential_election_*.tsv
run elections/elections_results.py

echo '----------------------------------------------------------------'
ls /Users/nuwan.senaratna/Not.Dropbox/_CODING/data/gig-data

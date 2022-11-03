function run { python3 src/gig_data_builder/$1; }

# country.tsv, province.tsv, district.tsv, dsd.tsv, gnd.tsv
run regions/admin_regions/admin_regions_basic_and_geo.py

# ed.tsv, pd.tsv
run elections/elections_basic.py

# moh.tsv
run regions/moh_basic_and_region_id_map.py

# lg.tsv
run regions/all_region_id_map_and_lg_basic.py

# census/data.*.tsv etc.
run census/census.py

echo '----------------------------------------------------------------'
ls /Users/nuwan.senaratna/Not.Dropbox/_CODING/data/gig-data

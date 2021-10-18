cd src/gig_data_builder

# Init
python3 init_dirs.py

# No Deps (except Init)
python3 elections_basic.py
python3 admin_regions_basic_and_geo.py
python3 moh_basic_and_region_id_map.py
python3 all_region_id_map_and_lg_basic.py

python3 census.py

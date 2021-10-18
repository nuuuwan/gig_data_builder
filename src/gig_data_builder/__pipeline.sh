DIR_SRC=src/gig_data_builder

# Init
python3 $DIR_SRC/init_dirs.py

python3 $DIR_SRC/elections_basic.py
python3 $DIR_SRC/admin_regions_basic_and_geo.py

python3 $DIR_SRC/moh_basic_and_region_id_map.py
python3 $DIR_SRC/all_region_id_map_and_lg_basic.py

python3 $DIR_SRC/census.py
python3 $DIR_SRC/non_admin_region_geo.py

python3 $DIR_SRC/basic_expand.py

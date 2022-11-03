function run { python3 src/gig_data_builder/$1; }

# Admin Regions: Ents & Geos
run regions/admin_regions/admin_regions_basic_and_geo.py

# MOH Regions: Ents & Geos
run regions/moh_basic_and_region_id_map.py

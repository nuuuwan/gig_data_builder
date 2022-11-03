function run { python3 src/gig_data_builder/$1; }

# Admin Regions: Create Ents and Geos
run regions/admin_regions/admin_regions_basic_and_geo.py

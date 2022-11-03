# GIG-Data Builder

GitHub repo [https://github.com/nuuuwan/gig](https://github.com/nuuuwan/gig) (GIG - Generalised Information Graph, containing various data about Sri Lanka) uses data stored in [https://github.com/nuuuwan/gig-data](https://github.com/nuuuwan/gig-data).

This repo contains various utility functions that populate [https://github.com/nuuuwan/gig-data](https://github.com/nuuuwan/gig-data), and their raw data sources (contained in directory [src/gig_data_builder/data_ground_truth](src/gig_data_builder/data_ground_truth)).

# Data Sources

* [statslmap](src/gig_data_builder/data_ground_truth/statslmap) contains TopoJSON files for each of Sri Lanka's Provinces, Administrative Districts, Divisional Secretariat Divisions and Grama Niladhari Divisions, and 2012 Census data for these regions.

* [region_id_map](src/gig_data_builder/data_ground_truth/region_id_map) contains known mappings between various types of regions.

* [elections](src/gig_data_builder/data_ground_truth/elections) contains Electoral District (ED) and Polling Division (PD) basic information.

* [moh](src/gig_data_builder/data_ground_truth/moh) contains Medical Officers of Health (MOH) Region Information.

* [elections_results](src/gig_data_builder/data_ground_truth/elections_results) results of presidential and parliamentary elections after 1978.

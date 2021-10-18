# GIG-Data Builder

GitHub repo [https://github.com/nuuuwan/gig](https://github.com/nuuuwan/gig) (GIG - Generalised Information Graph, containing various data about Sri Lanka) uses data stored in [https://github.com/nuuuwan/gig-data](https://github.com/nuuuwan/gig-data).

This repo contains various utility functions that populate [https://github.com/nuuuwan/gig-data](https://github.com/nuuuwan/gig-data), and their raw data sources (contained in directory [src/gig_data_builder/raw_data](src/gig_data_builder/raw_data)).

# Data Sources

* [statslmap](src/gig_data_builder/raw_data/statslmap) contains TopoJSON files for each of Sri Lanka's Provinces, Administrative Districts, Divisional Secretariat Divisions and Grama Niladhari Divisions, and 2012 Census data for these regions.

* [region_id_map](src/gig_data_builder/raw_data/region_id_map) contains known mappings between various types of regions.

* [elections](src/gig_data_builder/raw_data/elections) contains Electoral District (ED) and Polling Division (PD) basic information.

* [moh](src/gig_data_builder/raw_data/moh) contains Medical Officers of Health (MOH) Region Information.

# Excluded Data

* Alternate region codes
* Altitude

---

# Change History
* [2021-10-16 07:14AM] Added Raw Data: statslmap
* [2021-10-16 07:26AM] Build Basic Province, District, DSD, GND data
* [2021-10-16] Added Raw Data: region_id_map  
* [2021-10-16] Build Basic PD, ED, MOH, LG Data (Incomplete)
* [2021-10-16] Added Raw Data: elections
* [2021-10-17 04:39PM] Add LG Data
* [2021-10-17] Add MOH Data
* [2021-10-17] Add Geo Data for Admin Regions
* [2021-10-18 08:32AM] Add Census Data
* [2021-10-18 09:21AM] Added single pipeline
* [2021-10-18 10:36AM] Added Non-Admin Region Geos
* [2021-10-18 10:37AM] expand with ints etc
  *  [2021-10-18 10:37AM] Updated README
  *  [2021-10-18 11:28AM] Tested Pipeline
  *  [2021-10-18 01:26PM] Added utils

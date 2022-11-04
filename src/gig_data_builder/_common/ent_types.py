ADMIN_REGION_TYPES = ["province", "district", "dsd", "gnd"]
ELECTION_REGION_TYPES = ["ed", "pd"]
OTHER_REGION_TYPES = ["moh", "lg"]
REGION_TYPES = ADMIN_REGION_TYPES + ELECTION_REGION_TYPES + OTHER_REGION_TYPES

REGION_TYPE_TO_ID_LEN = {
    'province': 4,
    'district': 5,
    'dsd': 7,
    'gnd': 10,
}

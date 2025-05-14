import os

from utils import WWW, JSONFile
from utils_future import TSVFile

from gig_data_builder import _basic
from gig_data_builder._constants import DIR_DATA_GIG2, DIR_ELECTIONS_RESULTS
from gig_data_builder._utils import log

SUMMARY_STAT_KEYS = ["valid", "rejected", "polled", "electors"]
ELECTION_CONFIGS = {
    "local-government": {
        "year_list": [2025],
        "field_key_votes": "votes",
    },
    "parliamentary": {
        "year_list": [1989, 1994, 2000, 2001, 2004, 2010, 2015, 2020, 2024],
        "field_key_votes": "vote_count",
    },
    "presidential": {
        "year_list": [1982, 1988, 1994, 1999, 2005, 2010, 2015, 2019, 2024],
        "field_key_votes": "votes",
    },
}


def cmp_key(k):
    if k == "entity_id":
        return 0
    if k in ["valid", "rejected", "polled", "electors"]:
        return 1
    return 2


def expand_keys(idx):
    NON_PARTY_KEYS = ["entity_id", "valid", "rejected", "polled", "electors"]
    sorted_party_list = list(
        map(
            lambda x: x[0],
            sorted(
                list(
                    filter(
                        lambda x: x[0] not in NON_PARTY_KEYS,
                        idx["LK"].items(),
                    )
                ),
                key=lambda x: -x[1],
            ),
        )
    )

    expanded_data_list = []
    for d in idx.values():
        expanded_d = {}
        for k in NON_PARTY_KEYS + sorted_party_list:
            expanded_d[k] = d.get(k, 0)
        expanded_data_list.append(expanded_d)
    return expanded_data_list


def get_election_data_ground_truth_file(election_type, year):
    return os.path.join(
        DIR_ELECTIONS_RESULTS,
        f"{election_type}_election_{year}.json",
    )


def get_election_data_from_tsv_row(d):

    by_party = []
    for k, v in d.items():
        if k in SUMMARY_STAT_KEYS + ["entity_id", "timestamp"]:
            continue
        by_party.append(dict(party_code=k, vote_count=int(v)))

    pd_id = d["entity_id"]
    ed_id = pd_id[:5]

    if pd_id.endswith("P"):
        pd_code = "PV"
    else:
        pd_code = pd_id[3:]
    ed_code = ed_id[3:]

    return dict(
        type="RP_V",
        level="POLLING-DIVISION",
        pd_code=pd_code,
        ed_code=ed_code,
        by_party=by_party,
        summary=dict(
            electors=d["electors"],
            polled=d["polled"],
            valid=d["valid"],
            rejected=d["rejected"],
        ),
    )


def get_election_data_ground_truth_from_tsv(election_type, year):

    tsv_path = os.path.join(
        DIR_ELECTIONS_RESULTS,
        f"government-elections-{election_type}.regions-ec.{year}.tsv",
    )
    d_list = TSVFile(tsv_path).read()
    return [get_election_data_from_tsv_row(d) for d in d_list]


def get_election_data_ground_truth(election_type, year):
    if election_type == "parliamentary" and str(year) == "2024":
        return get_election_data_ground_truth_from_tsv(election_type, year)

    return JSONFile(
        get_election_data_ground_truth_file(election_type, year)
    ).read()


def get_election_data_file(election_type, year):
    return os.path.join(
        DIR_DATA_GIG2,
        f"government-elections-{election_type}.regions-ec.{year}.tsv",
    )


def main():  # noqa
    ed_data_index = _basic.get_basic_data_index(os.path.join("ents", ""), "ed")
    gnd_data_index = _basic.get_basic_data_index(
        os.path.join("ents", ""), "gnd"
    )
    lg_data_index = _basic.get_basic_data_index(os.path.join("ents", ""), "lg")
    pd_to_region_id_index = {}
    pd_to_pop = {}
    lg_to_region_id_index = {}
    lg_to_pop = {}
    for gnd_id, gnd in gnd_data_index.items():
        gnd_pop = (float)(gnd["population"]) if gnd["population"] else 0

        pd_id = gnd["pd_id"]
        if pd_id not in pd_to_region_id_index:
            pd_to_region_id_index[pd_id] = {}
            pd_to_pop[pd_id] = 0
        pd_to_region_id_index[pd_id][gnd_id] = gnd
        pd_to_pop[pd_id] += gnd_pop

        lg_id = gnd["lg_id"]
        if lg_id not in lg_to_region_id_index:
            lg_to_region_id_index[lg_id] = {}
            lg_to_pop[lg_id] = 0
        lg_to_region_id_index[lg_id][gnd_id] = gnd
        lg_to_pop[lg_id] += gnd_pop

    for election_type, config in ELECTION_CONFIGS.items():
        field_key_votes = config["field_key_votes"]
        for year in config["year_list"]:
            data_list = get_election_data_ground_truth(election_type, year)
            table = []

            # FOR EACH pd result
            for data in data_list:
                if election_type == "parliamentary" and data["type"] != "RP_V":
                    continue
                row = {}
                if election_type in ["presidential", "parliamentary"]:
                    if data["pd_code"] == "PV":
                        election_region_id = "EC-%s%s" % (data["ed_code"], "P")
                    elif data["pd_code"] == "DV":
                        election_region_id = "EC-%s%s" % (data["ed_code"], "D")
                    else:
                        election_region_id = "EC-%s" % (data["pd_code"])
                    election_region_id = election_region_id[:6]
                    row["entity_id"] = election_region_id
                elif election_type == "local-government":
                    lg_id = data["lg_id"]
                    row["entity_id"] = lg_id
                else:
                    raise ValueError(f"Unknown election type: {election_type}")

                for k in SUMMARY_STAT_KEYS:
                    row[k] = (int)(data["summary"][k])

                for for_party in data["by_party"]:
                    row[for_party["party_code"]] = (int)(
                        for_party[field_key_votes]
                    )
                table.append(row)

            # Expand to GNDs
            gnd_index = {}
            postal_and_displaced_rows = []
            for row in table:
                election_region_id = row["entity_id"]

                if election_type in ["presidential", "parliamentary"]:
                    election_region_to_pop = pd_to_pop
                    election_region_to_region_id_index = pd_to_region_id_index
                elif election_type == "local-government":
                    election_region_to_pop = lg_to_pop
                    election_region_to_region_id_index = lg_to_region_id_index
                else:
                    raise ValueError(f"Unknown election type: {election_type}")

                election_region_pop = election_region_to_pop.get(
                    election_region_id
                )
                if election_region_pop is None:
                    postal_and_displaced_rows.append(row)
                    continue

                for gnd_id, regions in election_region_to_region_id_index[
                    election_region_id
                ].items():
                    pop = (
                        (float)(regions["population"])
                        if regions["population"]
                        else 0
                    )
                    p_gnd = pop / election_region_pop

                    gnd_row = {"entity_id": gnd_id}
                    for k, v in row.items():
                        if k in ["entity_id"]:
                            continue
                        gnd_row[k] = (float)(v) * p_gnd
                    gnd_index[gnd_id] = gnd_row

            # Expand to Others
            parent_index = {}
            for gnd_id, gnd_row in gnd_index.items():
                for parent_type in [
                    "country",
                    "province",
                    "district",
                    "dsd",
                    "gnd",
                    "ed",
                    "pd",
                    "lg",
                ]:
                    if parent_type == "country":
                        parent_id = "LK"
                    else:
                        parent_id = gnd_data_index[gnd_id][parent_type + "_id"]

                    if parent_id not in parent_index:
                        parent_index[parent_id] = {"entity_id": parent_id}

                    for k, v in gnd_row.items():
                        if k in ["entity_id"]:
                            continue
                        if k not in parent_index[parent_id]:
                            parent_index[parent_id][k] = 0
                        parent_index[parent_id][k] += v

            # Add Postal and Displaced Votes to
            #   province, district, ed

            if election_type in ["presidential", "parliamentary"]:

                for row in postal_and_displaced_rows:
                    election_region_id = row["entity_id"]
                    ed_id = election_region_id[:5]
                    ed = ed_data_index[ed_id]
                    province_id = ed["province_id"]
                    country_id = "LK"

                    assert election_region_id not in parent_index
                    parent_index[election_region_id] = {
                        "entity_id": election_region_id
                    }

                    for k, v in row.items():
                        if k in ["entity_id"]:
                            continue
                        parent_index[election_region_id][k] = v
                        for parent_id in [
                            country_id,
                            province_id,
                            ed_id,
                        ]:
                            if k not in parent_index[parent_id]:
                                parent_index[parent_id][k] = 0
                            parent_index[parent_id][k] += v

            # Combine and Save
            table = expand_keys(parent_index)
            table = sorted(table, key=lambda d: d["entity_id"])

            table_file = get_election_data_file(election_type, year)
            TSVFile(table_file).write(table)
            n_data_list = len(table)
            log.info(f"Wrote {n_data_list} rows to {table_file}")


if __name__ == "__main__":
    main()

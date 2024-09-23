import os

from utils import WWW, JSONFile, TSVFile

from gig_data_builder import _basic
from gig_data_builder._constants import DIR_DATA_GIG2, DIR_ELECTIONS_RESULTS
from gig_data_builder._utils import log

SUMMARY_STAT_KEYS = ['valid', 'rejected', 'polled', 'electors']
ELECTION_CONFIGS = {
    'presidential': {
        'dir_remote': os.path.join(
            'https://raw.githubusercontent.com',
            'nuuuwan/elections_lk/data',
        ),
        'func_get_file': lambda year: f'elections_lk.presidential.{year}.json',
        'year_list': [1982, 1988, 1994, 1999, 2005, 2010, 2015, 2019, 2024],
        'field_key_votes': 'votes',
    },
    'parliamentary': {
        'dir_remote': os.path.join(
            'https://raw.githubusercontent.com',
            'nuuuwan/gen_elec_sl/master/elections_lk_react',
            'public/data/elections',
        ),
        'func_get_file': lambda year: f'gen_elec_sl.ec.results.{year}.json',
        'year_list': [1989, 1994, 2000, 2001, 2004, 2010, 2015, 2020],
        'field_key_votes': 'vote_count',
    },
}


def cmp_key(k):
    if k == 'entity_id':
        return 0
    if k in ['valid', 'rejected', 'polled', 'electors']:
        return 1
    return 2


def expand_keys(idx):
    NON_PARTY_KEYS = ['entity_id', 'valid', 'rejected', 'polled', 'electors']
    sorted_party_list = list(
        map(
            lambda x: x[0],
            sorted(
                list(
                    filter(
                        lambda x: x[0] not in NON_PARTY_KEYS,
                        idx['LK'].items(),
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
        f'{election_type}_election_{year}.json',
    )


def reverse_download():
    for election_type, config in ELECTION_CONFIGS.items():
        dir_remote = config['dir_remote']
        func_get_file = config['func_get_file']
        for year in config['year_list']:
            remote_url = os.path.join(
                dir_remote,
                func_get_file(year),
            )
            data = WWW(remote_url).readJSON()
            data_file = get_election_data_ground_truth_file(
                election_type, year
            )
            JSONFile(data_file).write(data)
            log.info(f'Downloaded from {remote_url} to {data_file}')


def get_election_data_ground_truth(election_type, year):
    return JSONFile(
        get_election_data_ground_truth_file(election_type, year)
    ).read()


def get_election_data_file(election_type, year):
    return os.path.join(
        DIR_DATA_GIG2,
        f'government-elections-{election_type}.regions-ec.{year}.tsv',
    )


def main():
    ed_data_index = _basic.get_basic_data_index(
        os.path.join('ents', ''), 'ed'
    )
    gnd_data_index = _basic.get_basic_data_index(
        os.path.join('ents', ''), 'gnd'
    )
    pd_to_region_id_index = {}
    pd_to_pop = {}
    for gnd_id, gnd in gnd_data_index.items():
        pd_id = gnd['pd_id']
        if pd_id not in pd_to_region_id_index:
            pd_to_region_id_index[pd_id] = {}
            pd_to_pop[pd_id] = 0
        pd_to_region_id_index[pd_id][gnd_id] = gnd
        pd_to_pop[pd_id] += (
            (float)(gnd['population']) if gnd['population'] else 0
        )

    for election_type, config in ELECTION_CONFIGS.items():
        field_key_votes = config['field_key_votes']
        for year in config['year_list']:
            data_list = get_election_data_ground_truth(election_type, year)
            table = []

            # FOR EACH pd result
            for data in data_list:
                if (
                    election_type == 'parliamentary'
                    and data['type'] != 'RP_V'
                ):
                    continue
                # PD
                row = {}
                if data['pd_code'] == 'PV':
                    pd_id = 'EC-%s%s' % (data['ed_code'], 'P')
                elif data['pd_code'] == 'DV':
                    pd_id = 'EC-%s%s' % (data['ed_code'], 'D')
                else:
                    pd_id = 'EC-%s' % (data['pd_code'])
                pd_id = pd_id[:6]
                row['entity_id'] = pd_id

                for k in SUMMARY_STAT_KEYS:
                    row[k] = (int)(data['summary'][k])

                for for_party in data['by_party']:
                    row[for_party['party_code']] = (int)(
                        for_party[field_key_votes]
                    )
                table.append(row)

            # Expand to GNDs
            gnd_index = {}
            postal_and_displaced_rows = []
            for row in table:
                pd_id = row['entity_id']
                pd_pop = pd_to_pop.get(pd_id)
                if pd_pop is None:
                    postal_and_displaced_rows.append(row)
                    continue
                for gnd_id, regions in pd_to_region_id_index[pd_id].items():
                    pop = (
                        (float)(regions['population'])
                        if regions['population']
                        else 0
                    )
                    p_gnd = pop / pd_pop

                    gnd_row = {'entity_id': gnd_id}
                    for k, v in row.items():
                        if k in ['entity_id']:
                            continue
                        gnd_row[k] = (float)(v) * p_gnd
                    gnd_index[gnd_id] = gnd_row

            # Expand to Others
            parent_index = {}
            for gnd_id, gnd_row in gnd_index.items():
                for parent_type in [
                    'country',
                    'province',
                    'district',
                    'dsd',
                    'gnd',
                    'ed',
                    'pd',
                ]:
                    if parent_type == 'country':
                        parent_id = 'LK'
                    else:
                        parent_id = gnd_data_index[gnd_id][
                            parent_type + '_id'
                        ]

                    if parent_id not in parent_index:
                        parent_index[parent_id] = {'entity_id': parent_id}

                    for k, v in gnd_row.items():
                        if k in ['entity_id']:
                            continue
                        if k not in parent_index[parent_id]:
                            parent_index[parent_id][k] = 0
                        parent_index[parent_id][k] += v

            # Add Postal and Displaced Votes to
            #   province, district, ed

            for row in postal_and_displaced_rows:
                pd_id = row['entity_id']
                ed_id = pd_id[:5]
                ed = ed_data_index[ed_id]
                province_id = ed['province_id']
                country_id = 'LK'

                assert pd_id not in parent_index
                parent_index[pd_id] = {'entity_id': pd_id}

                for k, v in row.items():
                    if k in ['entity_id']:
                        continue
                    parent_index[pd_id][k] = v
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
            table = sorted(table, key=lambda d: d['entity_id'])

            table_file = get_election_data_file(election_type, year)
            TSVFile(table_file).write(table)
            n_data_list = len(table)
            log.info(f'Wrote {n_data_list} rows to {table_file}')


if __name__ == '__main__':
    main()

import os

from utils import jsonx, tsv, www

from gig_data_builder._basic import get_basic_data_index
from gig_data_builder._constants import DIR_DATA_GIG2, DIR_ELECTIONS_RESULTS
from gig_data_builder._utils import log
from gig_data_builder.regions.all_region_id_map_and_lg_basic import \
    get_region_id_index

PARENT_TYPES = ['country', 'province', 'ed', 'district', 'dsd', 'lg', 'moh']

SUMMARY_STAT_KEYS = ['valid', 'rejected', 'polled', 'electors']
ELECTION_CONFIGS = {
    'presidential': {
        'dir_remote': os.path.join(
            'https://raw.githubusercontent.com',
            'nuuuwan/elections_lk/data',
        ),
        'func_get_file': lambda year: f'elections_lk.presidential.{year}.json',
        'year_list': [1982, 1988, 1994, 1999, 2005, 2010, 2015, 2019],
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
            data = www.read_json(remote_url)
            data_file = get_election_data_ground_truth_file(
                election_type, year
            )
            jsonx.write(data_file, data)
            log.info(f'Downloaded from {remote_url} to {data_file}')


def get_election_data_ground_truth(election_type, year):
    return jsonx.read(
        get_election_data_ground_truth_file(election_type, year)
    )


def get_election_data_file(election_type, year):
    return os.path.join(
        DIR_DATA_GIG2,
        f'government-elections-{election_type}.regions-ec.{year}.tsv',
    )


def main():
    ed_index = get_basic_data_index('ents/', 'ed')
    region_id_index = get_region_id_index()
    pd_to_region_id_index = {}
    pd_to_pop = {}
    for gnd_id, regions in region_id_index.items():
        pd_id = regions['pd_id']
        if pd_id not in pd_to_region_id_index:
            pd_to_region_id_index[pd_id] = {}
            pd_to_pop[pd_id] = 0
        pd_to_region_id_index[pd_id][gnd_id] = regions
        pd_to_pop[pd_id] += (
            (float)(regions['population']) if regions['population'] else 0
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
                        gnd_row[k] = (int)(v) * p_gnd
                    gnd_index[gnd_id] = gnd_row

            # Expand to Others
            parent_index = {}
            for gnd_id, gnd_row in gnd_index.items():
                for parent_type in PARENT_TYPES:
                    parent_id = region_id_index[gnd_id][parent_type + '_id']
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
                ed = ed_index[ed_id]
                province_id = ed['province_id']
                country_id = ed['country_id']

                for k, v in row.items():
                    if k in ['entity_id']:
                        continue
                    for parent_id in [
                        country_id,
                        province_id,
                        ed_id,
                    ]:
                        if k not in parent_index[parent_id]:
                            parent_index[parent_id][k] = 0
                        parent_index[parent_id][k] += v

            # Combine and Save
            table = (
                table + list(gnd_index.values()) + list(parent_index.values())
            )
            table = sorted(table, key=lambda d: -d['electors'])

            table_file = get_election_data_file(election_type, year)
            tsv.write(table_file, table)
            n_data_list = len(table)
            log.info(f'Wrote {n_data_list} rows to {table_file}')


if __name__ == '__main__':
    main()

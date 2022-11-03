import os

from utils import TSVFile, dt, jsonx, tsv

from gig_data_builder._constants import (DIR_DATA_GIG2, DIR_RAW_DATA,
                                         DIR_STATSL_DATA)
from gig_data_builder._utils import log
from gig_data_builder.regions.all_region_id_map_and_lg_basic import \
    get_region_id_index

METADATA_TABLES_FILE = os.path.join(DIR_STATSL_DATA, 'tables.json')
METADATA_FIELDS_FILE = os.path.join(DIR_STATSL_DATA, 'fields.json')


def get_table_name_to_file_name():
    data_list = TSVFile(os.path.join(DIR_RAW_DATA, 'census', 'census-met.tsv')).read()
    table_name_to_file_name = {}
    for d in data_list:
        table_name = d['table_name']
        m1 = d['measurement1']
        m2 = d['measurement2']
        e = d['entity']
        t = d['time']
        file_name_only = f'{m1}-{m2}.{e}.{t}.tsv'
        table_name_to_file_name[table_name] = os.path.join(
            DIR_DATA_GIG2, file_name_only
        )
    return table_name_to_file_name


def build():
    metadata_tables = jsonx.read(METADATA_TABLES_FILE)
    metadata_fields = jsonx.read(METADATA_FIELDS_FILE)
    region_id_index = get_region_id_index()
    table_name_to_file_name = get_table_name_to_file_name()

    for table_id, table_metadata in metadata_tables.items():
        field_metadata = metadata_fields[table_metadata['Filename']]

        # Build Table for GNDs
        table_file = os.path.join(
            DIR_STATSL_DATA, 'var_%s_gnd.json' % (table_id)
        )
        table_data = jsonx.read(table_file)
        table_data_list = []
        for gnd_id_num, gnd_table_data in table_data.items():
            d = {}
            d['entity_id'] = 'LK-%s' % (gnd_id_num)
            for field_id, value in sorted(
                gnd_table_data.items(),
                key=lambda x: (int)(x[0]),
            ):
                field_name = dt.to_snake(field_metadata[field_id])
                if str(value).isnumeric():
                    d[field_name] = (float)(value)
                else:
                    d[field_name] = 0
            table_data_list.append(d)

        # Expand for other regions
        parent_to_k_to_v = {}
        for d in table_data_list:
            gnd_id = d['entity_id']
            regions = region_id_index.get(gnd_id)
            if regions is None:
                log.error(f'No region info for gnd: {gnd_id}')
                continue

            for region_type in [
                'country',
                'province',
                'district',
                'dsd',
                'ed',
                'pd',
                'lg',
                'moh',
            ]:
                parent_id = regions.get(region_type + '_id', None)
                if parent_id is None or parent_id == '':
                    continue

                if parent_id not in parent_to_k_to_v:
                    parent_to_k_to_v[parent_id] = {}
                for k, v in d.items():
                    if k == 'entity_id':
                        continue
                    if k not in parent_to_k_to_v[parent_id]:
                        parent_to_k_to_v[parent_id][k] = 0
                    parent_to_k_to_v[parent_id][k] += v

        for parent_id, k_to_v in parent_to_k_to_v.items():
            table_data_list.append({**{'entity_id': parent_id}, **k_to_v})

        # Save
        table_data_list = sorted(
            table_data_list,
            key=lambda d: d['entity_id'],
        )
        n_table_data_list = len(table_data_list)

        table_name = dt.to_snake(table_metadata['Title'])
        table_file = table_name_to_file_name[table_name]
        tsv.write(table_file, table_data_list)
        log.debug(f'Writing {n_table_data_list} rows to {table_file}')


if __name__ == '__main__':
    build()

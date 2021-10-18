import os

from utils import dt, jsonx, tsv

from gig_data_builder._constants import DIR_DATA_CENSUS, DIR_STATSL_DATA
from gig_data_builder._utils import log

METADATA_TABLES_FILE = os.path.join(DIR_STATSL_DATA, 'tables.json')
METADATA_FIELDS_FILE = os.path.join(DIR_STATSL_DATA, 'fields.json')


def build():
    metadata_tables = jsonx.read(METADATA_TABLES_FILE)
    metadata_fields = jsonx.read(METADATA_FIELDS_FILE)

    for table_id, table_metadata in metadata_tables.items():

        field_metadata = metadata_fields[table_metadata['Filename']]

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

        table_data_list = sorted(
            table_data_list,
            key=lambda d: d['entity_id'],
        )
        n_table_data_list = len(table_data_list)

        table_name = dt.to_snake(table_metadata['Title'])
        table_file = os.path.join(DIR_DATA_CENSUS, 'data.%s.tsv' % table_name)
        tsv.write(table_file, table_data_list)
        log.info(f'Writing {n_table_data_list} rows to {table_file}')


if __name__ == '__main__':
    build()

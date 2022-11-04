from fuzzywuzzy import process as fuzzywuzzy_process

from gig_data_builder import _basic
from gig_data_builder._utils import log


def get_parent_to_field_to_ids(parent_region_type, field_key, region_type):
    if parent_region_type is not None:
        field_key_parent_id = parent_region_type + '_id'
    else:
        parent_id = 'LK'

    parent_to_field_to_ids = {}
    basic_data = _basic.get_basic_data(
        '_tmp/precensus-', region_type
    ) or _basic.get_basic_data('_tmp/precensus-pregeo-', region_type) or _basic.get_basic_data('_tmp/premoh-prelg-precensus-', region_type)

    for d in basic_data:
        id = d['id']
        if parent_region_type is not None:
            parent_id = d[field_key_parent_id]
        field_value = d[field_key]

        if parent_id not in parent_to_field_to_ids:
            parent_to_field_to_ids[parent_id] = {}
        if field_value not in parent_to_field_to_ids[parent_id]:
            parent_to_field_to_ids[parent_id][field_value] = []
        parent_to_field_to_ids[parent_id][field_value].append(id)
    log.debug(
        'Built parent_to_field_to_ids: '
        + f' {region_type}->{field_key}->{parent_region_type}'
    )
    return parent_to_field_to_ids


def fuzzy_match(search_text, field_to_ids):
    field_values = field_to_ids.keys()
    matches = fuzzywuzzy_process.extract(search_text, field_values, limit=1)
    if matches:
        matching_field_value = matches[0][0]
        return field_to_ids[matching_field_value][0]
    return None


class FuzzySearch:
    def __init__(self):
        self.index = {}

    @staticmethod
    def get_index_key(parent_type, region_type, search_field):
        return f'{parent_type}.{region_type}.{search_field}'

    def search(
        self, parent_type, parent_id, region_type, search_field, search_text
    ):
        index_key = FuzzySearch.get_index_key(
            parent_type, region_type, search_field
        )
        if index_key not in self.index:
            self.index[index_key] = get_parent_to_field_to_ids(
                parent_type, search_field, region_type
            )

        field_to_ids = self.index[index_key][parent_id]
        return fuzzy_match(search_text, field_to_ids)

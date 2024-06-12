from gig_data_builder._basic import store_basic_data
import os

def build_precensus_ent_for_country():
    store_basic_data(
        os.path.join('_tmp', 'precensus-'),
        'country',
        [
            {
                'id': 'LK',
                'country_id': 'LK',
                'name': 'Sri Lanka',
                'population': 20_357_776,
            }
        ],
    )


def main():
    build_precensus_ent_for_country()


if __name__ == '__main__':
    main()

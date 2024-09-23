import os
from utils import Log, JSONFile

log = Log('import_2024')

def main():
    DIR_DATA = r"C:\Users\ASUS\Dropbox\_CODING\py\prespollsl2024_py\data\ec\prod1"

    data_list = []
    for file_name in os.listdir(DIR_DATA):
        if not file_name.endswith('.json'):
            continue
        data = JSONFile(os.path.join(DIR_DATA, file_name)).read()
        if data['level'] not in ['POSTAL-VOTE', 'POLLING-DIVISION']:
            continue
        data_list.append(data)

    data_list.sort(key=lambda x: x['pd_code'])
    n = len(data_list)
    
    output_path = os.path.join('data_ground_truth', 'elections_results', 'presidential_election_2024.json')
    JSONFile(output_path).write(data_list)
    log.info(f'Wrote {n} items to {output_path}')

if __name__ == "__main__":
    main()
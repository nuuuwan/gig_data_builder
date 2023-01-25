import os

from utils import JSONFile, Log

DIR_VARIABLES = '_variables'

log = Log('StoredVariable')


class StoredVariable:
    def __init__(self, name, get_hot):
        self.name = name
        self.get_hot = get_hot

    @property
    def data_file_path(self):
        return os.path.join(
            DIR_VARIABLES,
            f'{self.name}.json',
        )

    def get(self):
        data_file = JSONFile(self.data_file_path)
        if data_file.exists:
            log.debug(f'Loaded {self.data_file_path}')
            return data_file.read()
        else:
            log.info(f'Generating hot data for "{self.name}"')
            data = self.get_hot()
            log.debug(f'Saved {self.data_file_path}')
            data_file.write(data)
            return data

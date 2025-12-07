import sys

from utils import Hash, Log

log = Log("utils_future.TSVFile")


class TSVFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def is_modified(self, new_data_list):
        h_new = Hash.md5(str(new_data_list))
        h_old = Hash.md5(str(self.read()))
        return h_new != h_old

    @staticmethod
    def stringify(data_list):
        return [{k: str(v) for k, v in d.items()} for d in data_list]

    def write(self, data_list):
        stringified_data_list = TSVFile.stringify(data_list)
        if not self.is_modified(stringified_data_list):
            log.debug(
                f"No changes detected in {self.file_path}. Skipping write."
            )
            return False
        with open(self.file_path, "w", encoding="utf8") as f:
            if len(stringified_data_list) > 0:
                f.write("\t".join(stringified_data_list[0].keys()) + "\n")
                for d in stringified_data_list:
                    f.write("\t".join(map(str, d.values())) + "\n")

        n = len(data_list)
        log.info(f"Wrote {n} records to {self.file_path}")

        return True

    def read(self):
        with open(self.file_path, "r", encoding="utf8") as f:
            lines = f.readlines()
            keys = lines[0].strip().split("\t")
            data_list = []
            for line in lines[1:]:
                values = line.strip().split("\t")
                data_list.append(dict(zip(keys, values)))
            return data_list


def test():
    import os

    tsv_file = os.path.join(
        "data_ground_truth",
        "census",
        "education-educational-attainment.expanded.tsv",
    )
    d_list = TSVFile(tsv_file).read()
    for d in d_list:
        print(d)
        print(d["region_type"])


if __name__ == "__main__":
    test()

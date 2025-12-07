from utils import Hash, Log

log = Log("utils_future.TSVFile")


class TSVFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def is_modified(self, new_data_list):
        hash_new = Hash.md5(str(new_data_list))
        hash_old = Hash.md5(str(self.read()))
        return hash_new != hash_old

    def write(self, data_list):
        if not self.is_modified(data_list):
            log.warning(
                f"No changes detected in {self.file_path}. Skipping write."
            )
            return False
        with open(self.file_path, "w", encoding="utf8") as f:
            if len(data_list) > 0:
                f.write("\t".join(data_list[0].keys()) + "\n")
                for d in data_list:
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

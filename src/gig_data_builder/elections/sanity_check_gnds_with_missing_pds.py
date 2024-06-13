import os

from gig import Ent, EntType
from utils import JSONFile, Log

log = Log('sanity_check_gnds_with_missing_pds')


def main():
    gnds = Ent.list_from_type(EntType.GND)
    gnds_without_pds = [
        gnd for gnd in gnds if not gnd.pd_id.startswith('EC-')
    ]
    n_gnds_without_pds = len(gnds_without_pds)
    log.debug(f'{n_gnds_without_pds} GNDs without PDs')

    dsd_id_set = set()
    for gnd in gnds_without_pds:
        dsd_id = gnd.dsd_id
        dsd_id_set.add(dsd_id)

    n_dsd_ids = len(dsd_id_set)
    log.debug(f'{n_dsd_ids} DSDs with GNDs without PDs')

    dsd_to_pd_to_n = {}
    for gnd in gnds:
        dsd_id = gnd.dsd_id
        if dsd_id not in dsd_id_set:
            continue
        pd_id = gnd.pd_id
        if dsd_id not in dsd_to_pd_to_n:
            dsd_to_pd_to_n[dsd_id] = {}
        if pd_id not in dsd_to_pd_to_n[dsd_id]:
            dsd_to_pd_to_n[dsd_id][pd_id] = 0
        dsd_to_pd_to_n[dsd_id][pd_id] += 1

    for dsd_id, pd_to_n in dsd_to_pd_to_n.items():
        pd_to_n = sorted(
            pd_to_n.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        log.debug(f'DSD {dsd_id}')
        for pd_id, n in pd_to_n:
            log.debug(f'  {pd_id}: {n}')

    gnd_id_to_pd_id = {}
    for gnd in gnds_without_pds:
        dsd_id = gnd.dsd_id
        pd_to_n = dsd_to_pd_to_n[dsd_id]
        pd_to_n = sorted(
            pd_to_n.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        top_pd_id = pd_to_n[0][0]
        gnd_id_to_pd_id[gnd.id] = top_pd_id
        log.debug(f'{gnd.id} -> {top_pd_id}')

    json_file_path = os.path.join(
        '_variables', 'missing_gnd_id_to_pd_id.json'
    )
    JSONFile(json_file_path).write(gnd_id_to_pd_id)
    log.info(f'Wrote {json_file_path}')


if __name__ == "__main__":
    main()

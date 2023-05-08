import pandas as pd


NULL_INT = -1
SLEEP_TIME = 0.1

ID_KEYS = ['location', 'rok_budowy', 'rooms', 'footprint']
PRINT_KEYS = ['title', 'full_price', 'per_meter_price', 'location', 'rok_budowy', 'rooms', 'footprint']

PARAMS = {}


def cleanup_number(string):
    return float(string.replace(' ', '').replace('\xa0', '').replace(',', '.'))


def deduplicate(database, id_keys=None, select_keys=None, verbose=False):
    if id_keys is None:
        id_keys = ID_KEYS
    if select_keys is None:
        select_keys = ['full_price']
    deduplicated = []
    for group, subtable in database.groupby(id_keys):
        deduplicated.append(subtable.sort_values(select_keys).iloc[0])
        if verbose and len(subtable) > 1:
            print(subtable[PRINT_KEYS])
            print()

    deduplicated = pd.DataFrame(deduplicated)
    return deduplicated
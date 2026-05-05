"""
Nigeria Geography Lookup
State and zone mappings from NDHS 2024 sstate variable
"""

ZONE_MAP = {
    1: 'North Central',
    2: 'North East',
    3: 'North West',
    4: 'South East',
    5: 'South South',
    6: 'South West',
}

ZONE_CODES = {
    'NC': 1, 'NE': 2, 'NW': 3,
    'SE': 4, 'SS': 5, 'SW': 6,
}

STATE_MAP = {
    1:  {'name': 'Sokoto',       'zone': 'NW', 'zone_code': 3},
    2:  {'name': 'Zamfara',      'zone': 'NW', 'zone_code': 3},
    3:  {'name': 'Katsina',      'zone': 'NW', 'zone_code': 3},
    4:  {'name': 'Jigawa',       'zone': 'NW', 'zone_code': 3},
    5:  {'name': 'Yobe',         'zone': 'NE', 'zone_code': 2},
    6:  {'name': 'Borno',        'zone': 'NE', 'zone_code': 2},
    7:  {'name': 'Adamawa',      'zone': 'NE', 'zone_code': 2},
    8:  {'name': 'Gombe',        'zone': 'NE', 'zone_code': 2},
    9:  {'name': 'Bauchi',       'zone': 'NE', 'zone_code': 2},
    10: {'name': 'Kano',         'zone': 'NW', 'zone_code': 3},
    11: {'name': 'Kaduna',       'zone': 'NW', 'zone_code': 3},
    12: {'name': 'Kebbi',        'zone': 'NW', 'zone_code': 3},
    13: {'name': 'Niger',        'zone': 'NC', 'zone_code': 1},
    14: {'name': 'FCT Abuja',    'zone': 'NC', 'zone_code': 1},
    15: {'name': 'Nasarawa',     'zone': 'NC', 'zone_code': 1},
    16: {'name': 'Plateau',      'zone': 'NC', 'zone_code': 1},
    17: {'name': 'Taraba',       'zone': 'NE', 'zone_code': 2},
    18: {'name': 'Benue',        'zone': 'NC', 'zone_code': 1},
    19: {'name': 'Kogi',         'zone': 'NC', 'zone_code': 1},
    20: {'name': 'Kwara',        'zone': 'NC', 'zone_code': 1},
    21: {'name': 'Oyo',          'zone': 'SW', 'zone_code': 6},
    22: {'name': 'Osun',         'zone': 'SW', 'zone_code': 6},
    23: {'name': 'Ekiti',        'zone': 'SW', 'zone_code': 6},
    24: {'name': 'Ondo',         'zone': 'SW', 'zone_code': 6},
    25: {'name': 'Edo',          'zone': 'SS', 'zone_code': 5},
    26: {'name': 'Anambra',      'zone': 'SE', 'zone_code': 4},
    27: {'name': 'Enugu',        'zone': 'SE', 'zone_code': 4},
    28: {'name': 'Ebonyi',       'zone': 'SE', 'zone_code': 4},
    29: {'name': 'Cross River',  'zone': 'SS', 'zone_code': 5},
    30: {'name': 'Akwa Ibom',    'zone': 'SS', 'zone_code': 5},
    31: {'name': 'Abia',         'zone': 'SE', 'zone_code': 4},
    32: {'name': 'Imo',          'zone': 'SE', 'zone_code': 4},
    33: {'name': 'Rivers',       'zone': 'SS', 'zone_code': 5},
    34: {'name': 'Bayelsa',      'zone': 'SS', 'zone_code': 5},
    35: {'name': 'Delta',        'zone': 'SS', 'zone_code': 5},
    36: {'name': 'Lagos',        'zone': 'SW', 'zone_code': 6},
    37: {'name': 'Ogun',         'zone': 'SW', 'zone_code': 6},
}

STATES_BY_ZONE = {}
for code, info in STATE_MAP.items():
    zone = info['zone']
    if zone not in STATES_BY_ZONE:
        STATES_BY_ZONE[zone] = []
    STATES_BY_ZONE[zone].append({'code': code, 'name': info['name']})

OUTCOMES = ['stunting', 'anaemia', 'wasting']
POPULATIONS = ['women', 'children', 'all']
GEO_LEVELS = ['zone', 'state']

if __name__ == "__main__":
    print("Nigeria Geography Lookup")
    print(f"Total states: {len(STATE_MAP)}")
    for zone, states in STATES_BY_ZONE.items():
        print(f"\n{zone} ({len(states)} states):")
        for s in states:
            print(f"  {s['code']:2d}. {s['name']}")

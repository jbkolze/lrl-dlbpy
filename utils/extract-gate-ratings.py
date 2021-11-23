from __future__ import with_statement
import DBAPI
import sys
import json

# Target directory for extracted ratings files
SAVE_DIR = r'C:/Temp/gate-ratings/'

main_gate_ids_standard = [
    '.Opening-MG1,Elev;Flow-MG1.Standard.Production',
]

main_gate_ids_tvl = [
    '.Opening-L1,Opening-MG1,Elev;Flow-MG1.Standard.Production',
    '.Opening-L2,Opening-MG2,Elev;Flow-MG2.Standard.Production',
]

bypass_ids_standard = [
    '.Opening-L1,Opening-BP1,Elev;Flow-BP1.Standard.Production',
    '.Opening-L2,Opening-BP2,Elev;Flow-BP2.Standard.Production',
]

bypass_ids_wfk = [
    '.Opening-L1,Opening-BP1,Elev;Flow-BP1.Standard.Production',
]

rating_locations = [
    'Barren',
    'Brookville',
    'Buckhorn',
    'CaesarCreek',
    'CaglesMill',
    'CarrCreek',
    'CaveRun',
    'CJBrown',
    'CMHarden',
    'Green',
    'Monroe',
    'Nolin',
    'Patoka',
    'Rough',
    'Taylorsville',
    'WestFork',
    'WHHarsha'
]

location_to_code = {
    'Barren': 'BRR',
    'Brookville': 'BVR',
    'Buckhorn': 'BHR',
    'CaesarCreek': 'CCK',
    'CaglesMill': 'CMR',
    'CarrCreek': 'CFK',
    'CaveRun': 'CRR',
    'CJBrown': 'CBR',
    'CMHarden': 'CHL',
    'Green': 'GRR',
    'Monroe': 'MNR',
    'Nolin': 'NRR',
    'Patoka': 'PRR',
    'Rough': 'RRR',
    'Taylorsville': 'TVL',
    'WestFork': 'WFR',
    'WHHarsha': 'WHL',
}


def build_rating(rating_id):
    print('Processing %s...' % rating_id)
    json_rating = {}
    rating_set = db.get(rating_id)

    rating_spec = rating_set.ratingSpecContainer
    ind_params = rating_spec.indParams

    table_rating = rating_set.abstractRatingContainers[-1]

    if any(x in ind_params[0] for x in ['L1', 'L2']):
        json_rating['isLevelDependent'] = True
        json_rating['rating'] = process_levels(table_rating)
    else:
        json_rating['isLevelDependent'] = False
        json_rating['rating'] = process_openings(table_rating)
    return json_rating


def process_levels(trc):
    level_dict = {}
    for rvc in trc.values:
        level = int(rvc.indValue)
        level_trc = rvc.depTable
        level_dict[level] = process_openings(level_trc)
    return level_dict


def process_openings(trc):
    rating_dict = {
        'openings': [],
        'elevations': [],
        'flows': []
    }
    for i, opening_rvc in enumerate(trc.values):
        opening = round(opening_rvc.indValue, 2)
        rating_dict['openings'].append(opening)
        opening_trc = opening_rvc.depTable
        flows = []
        for elev_rvc in opening_trc.values:
            if i == 1:
                elev = round(elev_rvc.indValue, 2)
                rating_dict['elevations'].append(elev)
            flow = round(elev_rvc.depValue, 0)
            flows.append(flow)
        rating_dict['flows'].append(flows)
    return rating_dict


def get_gate_name_from_id(rating_id):
    params = rating_id.split('.')[1]
    ind_params = params.split(';')[0]
    gate_param = ind_params.split(',')[-2]
    gate_name = gate_param[-3:]
    return gate_name


def get_filepath(location):
    return SAVE_DIR + location_to_code[location] + '.json'


def main():
    for location in rating_locations:
        if location == 'Taylorsville':
            mg_ids = main_gate_ids_tvl
        else:
            mg_ids = main_gate_ids_standard
        if location == 'WestFork':
            bp_ids = bypass_ids_wfk
        else:
            bp_ids = bypass_ids_standard
        ratings = {}
        for id_end in mg_ids + bp_ids:
            rating_id = location + id_end
            gate_name = get_gate_name_from_id(rating_id)
            rating = build_rating(rating_id)
            ratings[gate_name] = rating
        with open(get_filepath(location), 'w') as json_file:
            json.dump(ratings, json_file, indent=4, sort_keys=True)


if __name__ == '__main__':
    db = DBAPI.open()
    main()
    db.close()
    sys.exit(0)

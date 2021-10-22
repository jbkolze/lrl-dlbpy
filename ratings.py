import csv
from typing import List

CSV_DIR = './tests/data/'

def get_flow(project: str, elevation: float, mg1_opening: float, bp1_opening: float, bp2_opening: float, l1: float, l2: float, mg2_opening: float = 0):
    ratings = get_ratings(project)
    flows = []
    flows.append(rate_mg_flow(ratings, elevation, 'MG1', mg1_opening))
    print(flows)
    return sum(flows)

def rate_mg_flow(ratings: dict, elevation: float, gate: str, opening: float):
    try:
        rating = ratings[gate]
    except KeyError as err:
        err_msg = f'Gate "{gate}" not found in rating table. Available gates: {[key for key in ratings]}'
        raise KeyError(err_msg) from err

    opening_index = get_interp_index(rating['openings'], opening)
    if opening_index % 1 == 0:
        opening_flows = rating['flows'][opening_index]
    else:
        opening_flows = get_interp_list(rating['flows'], opening_index)
    elevation_index = get_interp_index(rating['elevations'], elevation)
    if elevation_index %1 == 0:
        flow = opening_flows[elevation_index]
    else:
        x = elevation_index
        flow = interp(x, int(x), int(x) + 1, opening_flows[int(x)], opening_flows[int(x) + 1])
    return round(flow)
    
def get_interp_index(list: List[float], value: float):
    if value in list:
        return list.index(value)
    elif value > list[0] and value < list[-1]:
        for x in range(len(list)):
            if list[x] > value:
                return interp(value, list[x - 1], list[x], x - 1, x)
    else:
        err_msg = f'Value of {value} outside of list limits: {list[0]} - {list[-1]}'
        raise ValueError(err_msg)

def get_interp_list(lists: List[List[float]], index: float):
    lower_index = int(index)
    upper_index = lower_index + 1
    lower_list = lists[lower_index]
    upper_list = lists[upper_index]
    weight = index % 1
    interp_list = []
    for a, b in zip(lower_list, upper_list):
        interp_list.append(a + (b - a) * weight)
    return interp_list

def interp(x: float, x0: float, x1: float, y0: float, y1: float):
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def get_ratings(project: str):
    ratings = {}
    with open(f'{CSV_DIR}{project}.csv') as csv_file:
        csv_reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        current_rating = None
        next_openings = False
        next_elevations = False
        for row in csv_reader:
            if next_openings:
                current_rating['openings'] = list(filter(str, row))
                next_openings = False
                next_elevations = True
                continue
            if next_elevations:
                current_rating['elevations'] = list(filter(str, row))
                next_elevations = False
                continue
            if isinstance(row[0], str):
                ratings[row[0]] = {}
                current_rating = ratings[row[0]]
                next_openings = True
                continue
            if not 'flows' in current_rating:
                current_rating['flows'] = []
            current_rating['flows'].append(list(filter(str, row)))
    return ratings


if __name__ == '__main__':
    flow = get_flow('BHR', 807.5, .67, 0, 0, 0, 0)
    print(f'Flow is: {flow}')
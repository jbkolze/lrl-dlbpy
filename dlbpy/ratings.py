import json
import pathlib
from typing import List, Optional

ofloat = Optional[float]
DATA_DIR = pathlib.Path('//COE-LRLDFE01LOU/ORG/ED/Public/DLB/dlbpy/ratings/')


class GateRatingSet:

    def __init__(self, project: str):
        self.project = project
        self.ratings = self.get_ratings()

    def get_ratings(self):
        with open(DATA_DIR/f'{self.project}.json') as json_file:
            ratings = json.load(json_file)
        return ratings

    def get_total_flow(self, elevation: float, mg1: ofloat = None, mg2: ofloat = None, bp1: ofloat = None, bp2: ofloat = None, l1: ofloat = None, l2: ofloat = None):
        flows = []
        gate_groups = [
            ('MG1', mg1, l1),
            ('MG2', mg2, l2),
            ('BP1', bp1, l1),
            ('BP2', bp2, l2),
        ]
        for gate_group in gate_groups:
            if gate_group[1]:
                flows.append(self.get_gate_flow(elevation, *gate_group))
        return sum(flows)

    def get_gate_flow(self, elevation: float, gate: str, opening: float, level: float = None):
        try:
            rating_header = self.ratings[gate]
        except KeyError as err:
            err_msg = f'{self.project}: Gate {gate} not found in rating table. Available gates: {[key for key in self.ratings]}'
            raise KeyError(err_msg) from err
        if rating_header['isLevelDependent'] is True:
            try:
                if level is None:
                    raise ValueError(f'{self.project}: Must provide intake level to calculate flow for {gate}')
                level_int = int(round(level,0))
                rating = rating_header['rating'][str(level_int)]
            except KeyError as err:
                err_msg = f'{self.project}: Gate {gate}: No rating found for intake level {level}.  Available levels: {[level for level in rating_header["rating"]]}'
                raise KeyError(err_msg) from err
        else:
            rating = rating_header['rating']
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


if __name__ == '__main__':
    grs = GateRatingSet('BHR')
    flow = grs.get_total_flow(807.5, mg1 = .15, bp1 = .8, bp2 = .6, l1 = 0, l2 = 0)
    print(f'Total flow: {flow}')
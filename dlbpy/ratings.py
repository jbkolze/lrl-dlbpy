"""Determine flows from JSON-formatted gate ratings data.

This module provide a GateRatingSet class to ingest gate rating data from a
JSON-formatted file.  Methods are provided to determine total flows or flows
per gate/bypass, but the primary intended use is to enter the elevation and
all gate settings into a single get_total_flows call that returns the total
outflow of the project.

Typical usage example:
    bhr = GateRatingSet()
    outflow = bhr.get_total_flow(785.5, mg1=0, bp1=1.0, l1=0, bp2=0.4, l2=0)

Attributes:
    ofloat (alias): Alias for optional float values (for missing/unused gates)
    DATA_DIR (Path): Path pointing to the directory that contains the
        JSON-formatted gate ratings data used for flow calculations.
"""

import json
import pathlib
from typing import List, Optional

ofloat = Optional[float]
DATA_DIR = pathlib.Path('//COE-LRLDFE01LOU/ORG/ED/Public/DLB/dlbpy/ratings/')


class GateRatingSet:
    """Retrieves JSON gate ratings data and computes outflows.

    When initialized, will read gate ratings data from a JSON-formatted file
    and populate the ratings dictionary attribute.  Flows can then be computed
    per gate or in total using the provided methods.

    Attributes:
        project (str): 3-letter project code, e.g. 'BHR'.
        ratings (dict): Retrieved gate ratings data.
    """

    def __init__(self, project: str):
        """Inits GateRatingSet for given project with corresponding gate rating data.

        Args:
            project (str): 3-letter project code, e.g. 'BHR'.
        """
        self.project = project
        self.ratings = self.get_ratings()

    def get_ratings(self):
        """Returns a gate ratings dictionary from the project's JSON file.

        Format of the returned dictionary is expected to be as follows:
            ratings: {
                isLevelDependent (bool),
                rating: [
                    opening1 (float): [
                        elev1 (float): flow1 (float),
                        elev2 (float): flow2 (float),
                        etc...
                    ],
                    opening2 (float): [elev:flow]
                    etc...
                ]
            }
            If rating is level-dependent, the 'rating' object will be a
            dictionary with integer keys representing the multi-level
            settings (0, 1, 2, etc...) and array values representing the
            corresponding opening/elevation/flow curves.
        """
        with open(DATA_DIR/f'{self.project}.json') as json_file:
            ratings = json.load(json_file)
        return ratings

    def get_total_flow(self, elevation: float, mg1: ofloat = None, mg2: ofloat = None, bp1: ofloat = None, bp2: ofloat = None, l1: ofloat = None, l2: ofloat = None):
        """Compute the project's total outflow from the elevation and gate settings.

        Any gates that are closed or unused at the project can be left out
        (defaulting to None) or set to 0.

        Args:
            elevation (float): Pool elevation in NGVD29.
            mg1 (ofloat, optional): Main Gate #1 opening in tenths. Defaults to none.
                Note: All projects except for TVL sum their total MG openings as MG1.
            mg2 (ofloat, optional): Main Gate #2 opening in tenths. Defaults to None.
            bp1 (ofloat, optional): Bypass #1 opening in tenths. Defaults to None.
            bp2 (ofloat, optional): Bypass #2 opening in tenths. Defaults to None.
            l1 (ofloat, optional): Multi-level intake #1 setting. Defaults to None.
            l2 (ofloat, optional): Multi-level intake #2 setting. Defaults to None.

        Returns:
            int: Total outflow based on the given elevation and gate settings.
        """
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
        """Computes the outflow from a single gate.

        Computes the outflow from a single gate given the corresponding pool elevation,
        gate opening, and multi-level setting (if required).

        Args:
            elevation (float): Pool elevation.
            gate (str): Abbreviated gate identifier.  Typical values are:
                'MG1', 'MG2', 'BP1', 'BP2'
            opening (float): Opening of the gate in tenths of total opening.
            level (float, optional): The corresponding multi-level setting. Not
                required if the rating isn't level-dependent.  Defaults to None.

        Raises:
            KeyError: The given gate and/or multi-level setting was not found in the 
                rating table.
            ValueError: No multi-level setting was given for level dependent rating.

        Returns:
            int: Calculated outflow based on gate rating and provided settings.
        """
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
    

def get_interp_index(list: List[float], value: float) -> int | float:
    """Returns the interpolated index of a value in the given list.

    Example:
        ex_list = [0, 5, 10, 15, 20]
        ex_value = 7
        x = get_interp_index(ex_list, ex_value)
        x == 1.4  # True

    Args:
        list (List[float]): A sorted list of floats.
        value (float): The value for which to compute an interpolated index.

    Raises:
        ValueError: The value was outside the bounds of the list.
    """
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
    """Returns an interpolated list of floats using a weighted index.

    A weighted index of 1.3 would compute an interpolated list between List[1] and
    List[2] that contains values 30% between the values in each list.

    Example:
        ex_list1 = [0, 10, 20]
        ex_list2 = [5, 15, 25]
        ex_lists = ex_list1 + ex_list2
        ex_index = 0.4
        x = get_interp_list(ex_lists, ex_index)
        x == [2, 12, 22]  # True

    Args:
        lists (List[List[float]]): A list of lists of floats from which a single
            interpolated list of floats will be computed.
        index (float): A weighted index used to interpolate the new list.
    """
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
    """Returns y given x, x0, x1, y0, and y1."""
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


if __name__ == '__main__':
    grs = GateRatingSet('BHR')
    flow = grs.get_total_flow(807.5, mg1 = .15, bp1 = .8, bp2 = .6, l1 = 0, l2 = 0)
    print(f'Total flow: {flow}')
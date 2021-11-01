import unittest
from dlbpy.ratings import GateRatingSet

test_list = []

# GRB
grr = GateRatingSet('GRR')
test_list.append([grr, 458, 674.24, .1, None, 0, 0, 6, 6])
nrr = GateRatingSet('NRR')
test_list.append([nrr, 1557, 507.27, .3, None, 0, 0, 0, 0])
brr = GateRatingSet('BRR')
test_list.append([brr, 3101, 548.74, .7, None, 0, 0, 0, 0])
test_list.append([brr, 3935, 548.74, .9, None, 0, 0, 0, 0])
rrr = GateRatingSet('RRR')
test_list.append([rrr, 1095, 488.60, .5, None, 0, 0, 0, 0])

# UKL
cfk = GateRatingSet('CFK')
test_list.append([cfk, 125, 1024.09, 0, None, 1, .6, 2, 2])
bhr = GateRatingSet('BHR')
test_list.append([bhr, 413, 777.58, 0.15, None, 0, 0, 0, 0])
test_list.append([bhr, 535, 777.58, .2, None, 0, 0, 0, 0])
crr = GateRatingSet('CRR')
test_list.append([crr, 510, 726.96, .1, 0, None, 0, 3, 2])

# MAB
wfr = GateRatingSet('WFR')
test_list.append([wfr, 35, 676.00, 0, None, 1, 0, 0, 0])
cbr = GateRatingSet('CBR')
test_list.append([cbr, 136, 1010.37, 0, None, 1, 1, 0, 0])
cck = GateRatingSet('CCK')
test_list.append([cck, 491, 847.58, 0, None, .6, .6, 2, 3])
test_list.append([cck, 246, 847.58, 0, None, .6, .6, 0, 3])
whl = GateRatingSet('WHL')
test_list.append([whl, 2077, 731.95, .5, None, 0, 0, 5, 5])
test_list.append([whl, 1238, 731.95, .3, None, 0, 0, 5, 5])

# MWB
chl = GateRatingSet('CHL')
test_list.append([chl, 109, 666.64, 0, None, 1.0, .7, 0, 0])
cmr = GateRatingSet('CMR')
test_list.append([cmr, 1099, 642.99, .5, None, 0, 0, 0, 0])
mnr = GateRatingSet('MNR')
test_list.append([mnr, 202, 538.43, .1, None, 0, 0, 2, 6])
prr = GateRatingSet('PRR')
test_list.append([prr, 260, 535.88, 0, None, .4, .4, 3, 5])

# SRB
tvl = GateRatingSet('TVL')
test_list.append([tvl, 465, 548.20, .05, .05, 0, 0, 7, 7])
test_list.append([tvl, 232, 548.20, .05, 0, 0, 0, 7, 0])

# WWB
bvr = GateRatingSet('BVR')
test_list.append([bvr, 1511, 745.43, .3, None, 0, 0, 3, 3])

class TestRatingFlows(unittest.TestCase):

    def test_matches_old_flow(self):
        for grs, flow, elev, mg1, mg2, bp1, bp2, l1, l2 in test_list:
            comp_flow = grs.get_total_flow(elev, mg1, mg2, bp1, bp2, l1, l2)
            with self.subTest(msg=f'Testing {grs.project}: {comp_flow} ?= {flow}', elev=elev, mg1=mg1, mg2=mg2, bp1=bp1, bp2=bp2, l1=l1, l2=l2):
                self.assertTrue(comp_flow > flow * .95)
                self.assertTrue(comp_flow < flow * 1.05)

if __name__ == '__main__':
    unittest.main()

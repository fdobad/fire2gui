#!python3
'''
https://stackoverflow.com/questions/28345780/how-do-i-create-a-python-namespace-argparse-parse-args-value


In [7]: from Cell2Fire.ParseInputs import ParseInputs as p

In [8]: pp = p()

In [9]: pp
Out[9]: Namespace(InFolder=None, OutFolder=None, sim_years=1, nsims=1, seed=123, nweathers=1, nthreads=1, max_fire_periods=1000, IgRadius=0, gridsStep=60, gridsFreq=-1, heuristic=-1, messages_path=None, GASelection=False, HCells=None, msgHeur='', planPath='', TFraction=1.0, GPTree=False, valueFile=None, noEvaluation=False, ngen=500, npop=100, tSize=3, cxpb=0.8, mutpb=0.2, indpb=0.5, WeatherOpt='rows', spreadPlots=False, finalGrid=False, verbose=False, ignitions=False, grids=False, plots=False, allPlots=False, combine=False, no_output=False, input_gendata=False, OutMessages=False, OutBehavior=False, PromTuning=False, input_trajectories=Fa...

'''
from argparse import Namespace
x = {'a': 1, 'b': 2}
ns = Namespace(**x)
print(ns.a) #output 1


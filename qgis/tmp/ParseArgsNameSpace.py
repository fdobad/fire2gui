#!python3
'''
https://stackoverflow.com/questions/28345780/how-do-i-create-a-python-namespace-argparse-parse-args-value

In [1]: from Cell2Fire.ParseInputs import ParseInputs as p

Out[2]: Namespace(InFolder=None, OutFolder=None, sim_years=1, nsims=1, seed=123, nweathers=1, nthreads=1, max_fire_periods=1000, IgRadius=0, gridsStep=60, gridsFreq=-1, heuristic=-1, messages_path=None, GASelection=False, HCells=None, msgHeur='', planPath='', TFraction=1.0, GPTree=False, valueFile=None, noEvaluation=False, ngen=500, npop=100, tSize=3, cxpb=0.8, mutpb=0.2, indpb=0.5, WeatherOpt='rows', spreadPlots=False, finalGrid=False, verbose=False, ignitions=False, grids=False, plots=False, allPlots=False, combine=False, no_output=False, input_gendata=False, OutMessages=False, OutBehavior=False, PromTuning=False, input_trajectories=False, stats=False, Geotiffs=False, tCorrected=False, onlyProcessing=False, BBO=False, cros=False, fdemand=False, pdfOutputs=False, input_PeriodLen=60, weather_period_len=60, ROS_Threshold=0.1, HFI_Threshold=0.1, ROS_CV=0.0, HFactor=1.0, FFactor=1.0, BFactor=1.0, EFactor=1.0, BurningLen=-1.0, ROS10Factor=3.34, CCFFactor=0.0, CBDFactor=0.0)
'''
from argparse import Namespace
x = {'a': 1, 'b': 2}
ns = Namespace(**x)
print(ns.a) #output 1

        params['InFolder'] = None
        params['OutFolder'] = None
        params['sim_years'] = 1
        params['nsims'] = 1
        params['seed'] = 123
        params['nweathers'] = 1
        params['nthreads'] = 1
        params['max_fire_periods'] = 1000
        params['IgRadius'] = 0
        params['gridsStep'] = 60
        params['gridsFreq'] = -1
        params['heuristic'] = -1
        params['messages_path'] = None
        params['GASelection'] = False
        params['HCells'] = None
        params['msgHeur'] = ''
        params['planPath'] = ''
        params['TFraction'] = 1.0
        params['GPTree'] = False
        params['valueFile'] = None
        params['noEvaluation'] = False
        params['ngen'] = 500
        params['npop'] = 100
        params['tSize'] = 3
        params['cxpb'] = 0.8
        params['mutpb'] = 0.2
        params['indpb'] = 0.5
        params['WeatherOpt'] = 'rows'
        params['spreadPlots'] = False
        params['finalGrid'] = False
        params['verbose'] = False
        params['ignitions'] = False
        params['grids'] = False
        params['plots'] = False
        params['allPlots'] = False
        params['combine'] = False
        params['no_output'] = False
        params['input_gendata'] = False
        params['OutMessages'] = False
        params['OutBehavior'] = False
        params['PromTuning'] = False
        params['input_trajectories'] = False
        params['stats'] = False
        params['Geotiffs'] = False
        params['tCorrected'] = False
        params['onlyProcessing'] = False
        params['BBO'] = False
        params['cros'] = False
        params['fdemand'] = False
        params['pdfOutputs'] = False
        params['input_PeriodLen'] = 60
        params['weather_period_len'] = 60
        params['ROS_Threshold'] = 0.1
        params['HFI_Threshold'] = 0.1
        params['ROS_CV'] = 0.0
        params['HFactor'] = 1.0
        params['FFactor'] = 1.0
        params['BFactor'] = 1.0
        params['EFactor'] = 1.0
        params['BurningLen'] = -1.0
        params['ROS10Factor'] = 3.34
        params['CCFFactor'] = 0.0
        params['CBDFactor'] = 0.0

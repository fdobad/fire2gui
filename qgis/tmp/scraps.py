
def getMatplotlibVersion():
    import matplotlib as m
    version=str(m.__version__)
    del m
    print('hello world matplotlib', version)
    return version

def loadVENV():
    venv='source '+c_dir+'/pyvenv/bin/activate'
    command=' ls && echo "hello world"'
    command=venv +' && '+ cmd

def runC2F():
    import sys, os
    print('current file',os.path.dirname(os.path.abspath(__file__)))
    print('current pwd',os.getcwd())
    print('sys.argv is empty', sys.argv[0])
    c_dir='/home/fdo/source/C2FSB'
    cmd='python3 '+c_dir+'/main.py --input-instance-folder '+c_dir+'/data/Hom_Fuel_101_40x40/ \
--output-folder '+c_dir+'/MyExperiment/ \
--nsims 5 \
--nthreads 2 \
--weather rows \
--ignitions \
--ROS-CV 0.5 \
--grids \
--output-messages \
--out-behavior \
--stats --allPlots \
--verbose'
    cmd=cmd.split(' ')
    import subprocess
    print(cmd)
    proc = subprocess.run( cmd, shell=True, capture_output=True, text=True, check=True )
    for line in proc.stdout.splitlines():
        print("stdout:", line)

def skipMain_directImport():
    from .C2FSB import main
    from Cell2Fire.ParseInputs import ParseInputs
    from Cell2FireC import *
    from Cell2Fire.Stats import *
    from Cell2Fire.Heuristics import *

def main():
    import subprocess
    subprocess.Popen(['qgis'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     shell=True)

if __name__ == '__main__':
    main()

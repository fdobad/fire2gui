from time import sleep
from sys import stderr #, stdout
from contextlib import redirect_stdout
#from tqdm import trange

with redirect_stdout(stderr):
    print('Hello World')
    #for i in trange(10):
    for i in range(10):
        print('out: %s'%i)
        print('err: %s'%i, file=stderr)
        sleep(0.5)
    print('Bye World')


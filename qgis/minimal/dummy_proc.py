from time import sleep
#from tqdm import trange
from sys import stderr

print('out Hello World')
print('err Hello World', file=stderr)
#for i in trange(10):
for i in range(20):
    print('out %s'%i)
    print('err %s'%i, file=stderr)
    sleep(0.5)
print('out Bye World')
print('err Bye World', file=stderr)


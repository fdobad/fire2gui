from time import sleep, time
from numpy import random
#from tqdm import trange

start = time()
print('Hello World start', start)

#for i in trange(10):
for i in range(20):
    print( 'doing stuff',i)
    sleep( 0.5+random.rand()*5)

print('Bye World end', time()-start)


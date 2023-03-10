import numpy as np
from glob import glob
import re
glob_pat = 'Grids/Grids[0-9]*/ForestGrid[0-9]*.csv'
re_pat = 'Grids([0-9]+)/ForestGrid([0-9]+)'
fl = glob( glob_pat)
num = np.fromiter( re.findall( re_pat, ' '.join(fl)), dtype=[('x',int),('y',int)])
sort = np.argsort( num , order=('x','y'))
num = np.array([ [ n[0], n[1] ] for n in num])[sort][::-1]
doindex = np.unique( num[:,0], return_index=True)[1]
fl = np.array(fl)
fl[sort][::-1][doindex]


fl = glob( glob_pat)
num = np.fromiter( re.findall( re_pat, ' '.join(fl)), dtype=[('x',int),('y',int)])
sort = np.argsort( num , order=('x','y'))[::-1]
num = np.array([ [ n[0], n[1] ] for n in num])[sort]
doindex = np.unique( num[:,0], return_index=True)[1]
fl = np.array(fl)[sort][doindex]
num = num[doindex]
fl,num


num = num[sortnum]
fl = np.array(fl)[sortnum]

numgroup = np.split(numarr[:, 1], np.unique(numarr[:, 0], return_index=True)[1][1:])
nummax = [ np.max(n) for n in numgroup]

num1, num2 = numarr.T
num1unq = np.unique( num1)

do = []
xr = 0
for x,y in num:
    if x!=xr:
        do += [True]
        xr=x
    else:
        do[-1]=False
        do += [True]

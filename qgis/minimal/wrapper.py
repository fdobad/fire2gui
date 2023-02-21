#!/bin/env python3
import sys, subprocess
print('wd:', sys.argv[1])
cmd = ['python3'] + sys.argv[2:]
print('cmd:', cmd)
p = subprocess.Popen( cmd, stdout=sys.stderr, stderr=sys.stderr, cwd=sys.argv[1])
p.wait()
print('Bye World')

'''
with redirect_stdout(sys.stderr):
from contextlib import redirect_stdout
from sys import argv, stderr #, stdout
from os import execl, chdir
from sys import executable
with redirect_stdout(stderr):
    print('Hello World argv', argv)
    print('1:', argv[1])
    print('2:', *argv[2:])
    chdir(argv[1])
    execl(executable, '-c', *argv[2:])
    print('Bye World')

'''

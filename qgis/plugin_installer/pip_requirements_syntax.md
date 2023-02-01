# Valid requirements.txt flavors
1.
```
# This is a comment, to show how #-prefixed lines are ignored.
# It is possible to specify requirements as plain names.
pytest
pytest-cov
beautifulsoup4

# The syntax supported here is the same as that of requirement specifiers.
docopt == 0.6.1
requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"
urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip

# It is possible to refer to other requirement files or constraints files.
-r other-requirements.txt
-c constraints.txt

# It is possible to refer to specific local distribution paths.
./downloads/numpy-1.9.2-cp34-none-win32.whl

# It is possible to refer to URLs.
http://wxpython.org/Phoenix/snapshot-builds/wxPython_Phoenix-3.0.3.dev1820+49a8884-cp34-none-win_amd64.whl
```
2. [environment markers](https://peps.python.org/pep-0345/#environment-markers)
```
python_version = ‘%s.%s’ % (sys.version_info[0], sys.version_info[1])
python_full_version = sys.version.split()[0]
os.name = os.name
sys.platform = sys.platform
platform.version = platform.version()
platform.machine = platform.machine()
platform.python_implementation = platform.python_implementation()
a free string, like '2.4', or 'win32'

'python_version' | 'python_full_version' |
                 'os_name' | 'sys_platform' | 'platform_release' |
                 'platform_system' | 'platform_version' |
                 'platform_machine' | 'platform_python_implementation' |
                 'implementation_name' | 'implementation_version' |
                 'extra' # ONLY when defined by a containing layer
```
3. TOTEST?
```
--index-url https://pypi.python.org/simple/
-e https://github.com/foo/bar.git#egg=bar
-e .
imread; sys_platform == "unix"
imread-0.7.4-cp39-cp39-win_amd64.whl; sys_platform == "unix"
```
# References
https://pip.pypa.io/en/stable/reference/requirements-file-format/
https://peps.python.org/pep-0508/#grammar
https://peps.python.org/pep-0345/#environment-markers
https://caremad.io/posts/2013/07/setup-vs-requirement/
https://pip.pypa.io/en/stable/user_guide/#requirements-files

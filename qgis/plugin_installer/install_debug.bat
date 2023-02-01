ECHO :: Fire2Maa says :: Welcome to the plugin installer
ECHO.

REM CALL "C:\OSGeo4W\bin\o4w_env.bat" || ECHO :: Fire2Maa says :: Qgis Environment failed
IF %ERRORLEVEL% neq 0 goto ProcessError

REM python -m pip install --upgrade setuptools wheel pip || ECHO :: Fire2Maa says :: Upgrading pip & tools failed
IF %ERRORLEVEL% neq 0 goto ProcessError

REM pip install -r requirements.txt || ECHO :: Fire2Maa says :: Installing python packages failed
IF %ERRORLEVEL% neq 0 goto ProcessError

IF "%~1"=="" (
python -c "import sys; print(sys.executable); import site; print(site.getsitepackages())"
python -c "import fastparquet; print('fastparquet:',fastparquet.__version__)"
python -c "import imread; print('imread:',imread.__version__)"
)

REM IF EXIST "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\Fire2aam" RMDIR /s /q "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\Fire2aam"
REM XCOPY /e /k /h /i /q "Fire2aam" "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\Fire2aam"
IF EXIST "dummyPluginFolder\Fire2aam\" RMDIR /s /q "dummyPluginFolder\Fire2aam"
XCOPY /e /k /h /i /q "Fire2aam" "dummyPluginFolder\Fire2aam"
IF %ERRORLEVEL% neq 0 goto ProcessError

REM happy ending
ECHO.
COLOR 2
ECHO :: Fire2Maa says :: Success
PAUSE
exit /b 0

:ProcessError
REM process error
ECHO.
COLOR 4
ECHO	:: Fire2Maa says :: Errors were made
ECHO	Please run 'install_debug.bat' & report the issue at https://www.github.com/fire2aam/fire2aam-qgis-plugin/issues
PAUSE
exit /b 1

@ECHO OFF
:: Check for Python Installation

goto :CHECKPYTHON

:CHECKPYTHON
python --version 3>NUL
if errorlevel 1 goto NoPython
goto :HasPython

:NoPython
ActivePython-3.8.1-amd64.exe
goto :CHECKPYTHON

:HasPython
QGIS --version 3>NUL
if errorlevel 1 goto NoQgis
goto :HasQgis

:NoQgis
ActiveQGIS-OSGeo4W-3.4.15-1Setupx86_64.exe
goto :HasQgis

:HasQgis
start QGIS
goto eof

:: Once done, exit the batch file


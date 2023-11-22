# logunittest
<b>PIPENV enabled 'pytest' logging tool. </b>

Runs and logs your test results from pytest. Assumes <b>Pipenv environment</b> and 
tests for single or multiple packages using <b>'pytest'</b>.
Also, tests can be run in a tox style using multiple python versions. Additionally you can
group tests together in order to test dependency packages that you controll.

<img src="https://drive.google.com/uc?id=1C8LBRduuHTgN8tWDqna_eH5lvqhTUQR4" alt="me_happy" class="plain" height="150px" width="220px">

### run in Terminal
```
    lut $action -p --pgDir [/dir/to/tgt] -m comment-c | actions: info, ut, tox

    # Examples
    lut ut [-m:str "comment to be added to log file"] [-c:bool cleanup logs] [-p:str pgDir]
    lut tox (note -m does not work with the tox action)
    lut stats
```
NOTE: if pgDir is omitted os.getcwd() is used
NOTE: if you use the -p:str pgDir option, you can run 'pytest' for any package targeted by pgDir
After running lut, the test results are logged in the settings.defaultLogDir directory.
NOTE: if you dont provide a -i:str testId lut will create a new testId for every test run.

## System preconditions
Currently assumes you are using pipenv.
NOTE: You cannot have a .venv directory within your project directory as it will prevent logunittest from creating a .venv file.

## Why use this?
My main objective was to have a non blocking testing mechanism within a CI/CD chain. Test results are logged and any subsequent actions are derrived from the created logs.
Also I didnt get tox to properly install and activate multiple test environments without interferring with my development environment. This application installs pipenvs the tox way but also creates relevant temp files and changes relevant parameters to properly activate them. 


## Steps to setup
1. get and install logunittest
2. create a tox.ini next to your Pipfile (same directory)
3. in your terminal instead of unittest/pytest you now run logunittest (lut) as shown above

The tests will be run and test results are logged inside the created log file.

# get and install
```shell
    git clone git@github.com:lmielke/logunittest.git

```

## Pipfile [packages]
Directly install from git via the Pipfile entry below.
logunittest = \{git = "git@github.com:lmielke/logunittest.git"\}


## Tox.ini example

```ini

[tox]
envlist = py310, py311, py312

[testenv]
install_command = pipenv install --dev
test_command = pipenv run lut ut -c

[logunittest]
pgList = ~/python_venvs/packages/logunittest
defaultLogDir = ~/.testlogs
logPreserveThreshold = {'days': 20, 'count': 20}
verbose = 3 # default is 1

```

## Logs directory/location
- fileName like: logunittest_2023-11-21-15-37-47_py3.11.6_test-err-2_.log
- fileHead: 
```log
11-20 17:30 INFO logunittest - log_results: logunittest
unittest summary: [all:7 ok:7 err:0]
```

## logfile head
- fileHead can be extracted using logunittest.py.Coverage
- see test_logunittest.py for examples

<img src="https://drive.google.com/uc?id=1CDYXO_5Y5vKFGyVjYx4ne7GXJNyjzSG1" alt="terminal_bar" class="plain" height="100px" width="700px">
<b>Example log file extract used in terminal</b>

## Developer info
### logunittest
- logunittest/\__main__.py is entry point and calls a module from logunittest.actions
- 'lut ut' will os.chdir() into the pgDir and then run your tests
- tests will be run using subprocess call and stdout and stderr are returned

## Runntime states
During testing logunittest will temporarily change some settings within your pipenv project.
1. lut tox will create a .tox directory where your testable environments are installed.
2. A .venv file is created/changed so that 'pipenv run' can find the test environment for every test form envList that will be run. See tox.ini
3. The Pipfile is changed. Insid the \[requires\] block the python_version parameter is changed to the current python version (i.e. py3.11) to be tested. See tox.ini

All the file changes will be reversed after the test is finished. In case of errors you might check these files for any residuals. (Pipfile, .venv, .tox)
The .tox directory will remain intact and will be reused for subsequent tests. (In case of errors you can always remove the .tox directory and subdirectories 'rm .tox \[-r -force\]')

Run like:
```shell
    cd yourPackageDir
    lut tox
```

## Coverage Infos
To display some stats from last tests use "lut stats" command.

## Grouping tests like tox
Tests can be grouped together in order to test dependency packages you own and controll.
- create one or multiple app directories inside defaultLogDir. (i.e. ~/.testlogs/my_app0).
- Inside the my_app0 directory create a tox.ini file like shown above.
- in tox.ini \[logunittest\] add a pgList i.e. pgList = ~/python_venvs/packages/package1, ...)

You can then run logunittest like so:
```shell
    lut ut -a my_app
```
This will test the package and also the dependencies as specified in pgList. The test results will be logged in the apps log directories.


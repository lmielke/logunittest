# logunittest runs and logs your python -m unittest

<img src="https://drive.google.com/uc?id=1C8LBRduuHTgN8tWDqna_eH5lvqhTUQR4" alt="me_happy" class="plain" height="150px" width="220px">

## Work with logunittest
- get and install logunittest
- create logs directory in your package folder
- run in Shell logunittest instead of unittest

## get and install
```
    git clone git@gitlab.com:larsmielke2/logunittest.git
```

## Pipfile
logunittest = {git = "https://gitlab.com/larsmielke2/logunittest.git"}

### run in Shell
```
    lut $action -p --targetDir [/dir/to/tgt] actions: info, ut
    # Example
    lut ut -p '.'
```
NOTE: if targetDir is omitted os.getcwd() is used

## logs directory
- location: Readme.md.directory/logunittest/test/logs
- fileName like: logunittest_2022-11-29-15-01-35-672179.log
- fileHead: 11-29 15:01 INFO logunittest - run_unittest: summary: [all:4 ok:3 err:1]

## logfile head
- fileHead can be extracted using logunittest.py.Coverage
- see test_logunittest.py for examples

## Developer info
### logunittest
- logunittest/\__main__.py serves as the lut entry point and calls module in logunittest/actions, see setup.cfg
- 'lut ut' will os.chdir() into the targetDir and then run: 'pipenv run python -m unittest' within the targetDir

## Runntime state
Tests can be run using different runntime states such as Pipfile sources or db connections.
You might implement a git_sync action that syncs after sucessfully running ut.
Currently only one single change is alpha implemented:
- Pipfile sources can vary between git source vs. local path source ('rm' == git source)
- changes the Pipfile temporarily from local path source to git source
- this can be usefull if a push to git requires the source to change
- running "lut pipfile -r rm" will temporarily change the Pipfile

## Coverage Infos
To display some stats from last tests use "lut stats" command.
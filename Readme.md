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
    lut ut -g # will commit chanes using git_sync
    lut ut -g -m 'add a git comment' #default: 'lut push with auto-comment [all:2 ok:2 err:0]'
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




# Gitlab Pipline Testing as static docu :)
A docker image with the name 'unittests' is used to allow running unittests for all gitlab projects.
- lcation: dockerhub lmielke/unittests
- tags: latest
```
    # tag and push the image to dockerhub
    docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD docker.io
    docker tag 2023-01-31_experimental_logunittest_up:latest lmielke/unittests:latest
    docker push lmielke/unittests:latest
```

## Gitlab-Runner
Uses a digitalocean droplet, which hosts the registered gitlab-runners and uses docker to run the unittest container.

### Install runner droplet

On your local machine:
```
    # create droplet on digitalocean
    cda $base
    python .\modules\os_setup\droplet\mkandinstall.py all -prc microservice -con scp -pd runners -cn testing -n testserver -pr runners -d
```

Inside runners droplet:
```
    # use apps/runners to login to runners droplet
    git clone https://$GIT_ACCESS_TOKEN@gitlab.com/larsmielke2/os_setup.git ./modules/os_setup
    
    # install gitlab-runner (no params), NOTE: lines worked but script is not tested
    bash ./modules/os_setup/linux/gitlab_runner/gitlab_runner_installs.sh
```

### Register the runner:
From keepass/apps/logunittest create a COPY of 'gitlab-runner register' to your projects entry_group.
- Change 'title'
- in entry/advanced >> {S:NAME} set the runner name i.e. like 'projectName_runner'!
Then go to web gitlab/project >> settings >> runner to optain and copy the 'runner token' into the 'password' field.

Next: login to 'runners' droplet as root and execute autotype for 'gitlab-runner register'. You can then go to gitlab/project >> settings >> runner and you should see the new runner.
NOTE: if the runner remains unactive run:
```
   # run where gitlab-runner is installed to check existing runners and refresh connection
   gitlab-runner verify
```
Ones the runner is marked as green, you can use it.

### Configure your gitlab project
Go to your project >> settings >> ci/cd >> variables and create the following variables.
- $CI_REGISTRY_USER: lmielke
- $CI_REGISTRY_PASSWORD: keepass
- $CI_REGISTRY: docker.io

Copy a .gitlab-ci.yml file from logunittest to your project root directory.

__Congrats, You can now commit !__

## Running the unittest image manually
Sometimes it might be needed to run unittest maunally.
The image uses a entrypoint.sh as (dockerfile ENTRYPOINT), which then calls specific entrypoint_package.sh (package comes from dockerfile CMD) scripts to run tests and other functions.
In docker run you can add the testing parameter at the end - after the image name. This will overwrite CMD and passes paramters to the entrypoint.sh script.
Parameters are as follows (provided as '*args' no commas ):
- the entrypoints fileName extension (i.e. unittest -> entrypoint_unittest.sh)
- packageName (i.e. joringels)
- no-update (default is update)

Example:
```
    # docker run unittest for joringels no-update
    docker run -it --rm --ip 172.18.0.9 --network illuminati 2023-01-31_experimental_logunittest_up unittest joringels no-update
    # using the dockerhub image
    docker run -it --rm --ip 172.18.0.9 --network illuminati lmielke/unittests:latest unittest logunittest no-update
```

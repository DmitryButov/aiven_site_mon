# Aiven Site Monitor - Developer guide

>  Doc Status: [Draft, intro for developers]

## Project structure

- src - source folder
  - aiven_site_mon - main package
    - we have `__main__.py` to have ability to run it as `python3 -m aiven_site_mon` for developing porposes
    - requirements.txt - list of external packages fo be installed for development
    - sub-packages: common, consumer, producer
- tests - folder for tests for pytest. Not a part of a `aiven_site_mon` package. Need for testing `aiven_site_mon` package after installing (in virtual env on developer machine)
- scripts - command line tools which can run as Linux-bash command (deprecated, now we directy create cli tool from setup.py)
- docs - additional docs for project. This file is located there
- examples. Holds example of settings files for producer and consumer
- readme.md
- LICENSE file (MIT)

### Python version

This product developing on Python 3.6.9

## Branches

- `master` - stable branch. To migrate to this branch we need add tests
- `develop` - mainstream branch for development, we merge new features into it
- `feature/new_cool_feature` - for adding every new functionality please use a separate branch. We will merge it into develop branch after pull request.

## Install & start development

- install process controlled from file `setup.py` in the root folder of project

- in first, in root project folder, create and activate virtual environment

  ```sh
  python3 -m venv env
  source env/bin/activate
  ```

- for install in development mode (with ability to edit code without reinstall), please use command

  ```sh
  python3 -m pip install --editable .
  ```

> Note: you can find more details about installing packages and usage virtual environment inside [this guide](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

## Usage examples

Linux shell:

```bash
# get help and usage
aiven_site_mon
aiven_site_mon --help
# check version
aiven_site_mon --version
#start in console mode with advanced.json settings file and log level = TRACE
aiven_site_mon --mode console --settings examples/settings/advanced.json -l TRACE
# run producer (mode yet not implemented!)
#aiven_site_mon --mode=kafka-producer --settings=settings.json
# run consumer (mode yet not implemented!)
#aiven_site_mon --mode=kafka-consumer --settings=settings.json

```

Or we can run by using python3 command

```bash
python3 -m aiven_site_mon
```

## Knowledge base

There are collected useful suitable articles and code examples, which were partially used for create current solution:

- [Multiprocessing vs. Threading in Python: What you need to know](https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/)

- [example from multiprocessing Pool and KeyboardInterrupt handling](https://github.com/jreese/multiprocessing-keyboardinterrupt)

- [aiven-examples](https://github.com/aiven/aiven-examples)

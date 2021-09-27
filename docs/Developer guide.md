# Aiven Site Monitor - Developer guide

>  Doc Status: [Draft, intro for developers]

## Project structure

- src - source folder
  - aiven_site_mon - main package
    - we have `__main__.py` to have ability to run it as `python3 -m aiven_site_mon`
    - sub-packages: common, consumer, producer
- tests - folder for tests for pytest. Not a part of a `aiven_site_mon` package. Need for testing `aiven_site_mon` package after installing (in virtual env on developer machine)
- scripts - command line tools which can run as Linux-bash command (script)
- docs
- examples. Holds example of settings files for producer and consumer
- readme.md
- LICENSE file (MIT)

## Install

- use setup.py in the root folder of project

## Usage examples

Linux shell:

```bash
# get help and usage
aiven_site_mon
aiven_site_mon --help
# check version
aiven_site_mon --version
# run producer
aiven_site_mon --mode=kafka-producer --settings=settings.json
# run consumer
aiven_site_mon --mode=kafka-consumer --settings=settings.json
```

Or we can run by using python (this is a single way to run for Windows)

```bash
python3 -m aiven_site_mon
```

>  Note: For developing it's recommended to use [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

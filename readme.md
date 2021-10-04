# Aiven Site Monitor

> Doc Status - [Draft]. Application is under development

**The system monitors websites availability over the network, produces metrics about this and passes these events through an Aiven Kafka instance into an Aiven PostgreSQL database.**

This project can be considered by test application for Aiven services. You can register to Aiven platform by using this link https://console.aiven.io

## How it should work 

- a Kafka producer periodically checks the target websites and sends the check results to a Kafka topic
- a Kafka consumer storing the data to an Aiven PostgreSQL database

The website monitor perform the periodically checks:

- the HTTP response time

- status code returned

- as well as optionally checking the returned page contents for a regexp pattern that is expected to be found on the page.

  > Note: Application is under development.
  > At this moment we support only console website monitor without communication with Kafka. Also you can select one of 2 load_balancing_policy (see details in settings description)

## Getting Started

- clone this repository and go into root folder

- install  package

  ```sh
  python3 -m pip install .
  ```

- from this moment you can use `aiven_site_mon` tool, you can check version of this tool by using command:

  ```
  aiven_site_mon --version
  ```

- Create a  `settings.json` file with list of sites and necessary settings. You also can use/modify one of example files from `examples/settings`  directory.  You can see example below. 

    > Note: See detailed description of settings file format in corresponding part of this guide.  

- start tool (site monitor)

  ```sh
  aiven_site_mon --settings settings.json
  ```

- You can see results in console log.

## Command line arguments

You can see full list of arguments by typing:

```sh
aiven_site_mon --help
```

Most important arguments:

- `-v` or  `--version` -  get aiven_site_mon version
- `-s ` or `--settings` for select settings json file. This arg is required
- `-m ` or `--mode` - operating mode. Tool can be launched in 3 modes:
  - `console` - site monitor with output to command-line
  - `kafka-producer` - this mode not implemented now! under developing
  - `kafka-consumer`-  this mode not implemented now! under developing

Usage example:

```sh
#start in console mode with advanced.json settings file and log level = TRACE
aiven_site_mon --mode console --settings examples/settings/advanced.json -l TRACE
```

## Settings file

Example of settings json file content:

```json
{
    "producer": {
        "update_period_sec": 10,
        "load_balancing_policy": "round_robin",
        "process_count": 2,
        "sites": [
            {
                "url": "https://example.com",
                "pattern": "<title>(.+)</title>"
            },
            {
                "url": "https://aiven.io/",
                "pattern": ""
            },
            {
                "url": "https://aiven.io/about",
                "pattern": "<title>(.+)</title>"
            }
        ]
    }
}
```

Settings related with site monitoring collected in `producer`:

- `sites` - array of site objects. Each site contain site `url` and search `pattern`. You can set a pattern for search some content by regex. If pattern is not needed, just use empty sting as `pattern` value
- `update_period_sec` - update period if each site in seconds. if not specified, the default will be used: 3 seconds
- `process_count` - amount of parallel processes.  If not specified, the default will be used. By default process count is equal to CPU cores in system.
- `load_balancing_policy`  Used for managing load to CPUs.  Supported values: `round_robin` , `compressed`.  If not specified, the default will be used. Default value is `round_robin` . See details below.

> Note: Application is under development.
> We will add more details as the project develops.

### Load balancing policy

Load balancer use for managing load to CPUs and for managing time intervals between request.  

Supported 2 load balancing policies:

- **Round Robin**
  - select in settings:  `"load_balancing_policy": "round_robin"`
  - Requests are evenly spread over time.
  - Each site from list checks separately from others at regular update time intervals (`update_period_sec`).  Time spread between requests calculated as site update period divided by amount of sites in list.
  - CPU load is balanced.
- **Compressed (general snapshot)**
  - select in settings:  `"load_balancing_policy": "compressed"`
  - Requests are compressed in time.
  - The goal of this policy is to check all sites from list together, in the shortest possible time. This approach allows to create a general snapshot of site's state with binding to one time point.
  -  CPU load is not balanced! It periodically increases to high values on polling timepoints.

## For developers

Please, see **Developer guide** inside `docs` directory of this project


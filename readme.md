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

## Quick Start

```sh
python3 src/aiven_site_mon/producer/site_mon.py
```

## Getting Started Guide

- Create a  settings.json file with list of necessary sites, or modify an existing file, and put it into `src/producer` directory. Also, optionally, you can set a pattern for search some content by regex. If pattern is not needed, just use empty string.

  Example:

  ```json
  {
      "sites": [
          {
              "url": "https://example.com",
              "pattern": "<h1>(.+)</h1>"
          },
          {
              "url": "https://example.com",
              "pattern": "<title>(.+)</title>"
          },
          {
              "url": "https://aiven.io/",
              "pattern": ""
          }
      ]
  }
  ```

- start producer (site monitor)

  ```sh
  python3 src/producer/site_mon.py
  ```

  You can see results in console log.

> Note: Application is under development
> We will add more details as the project develops.

## Branches

- `master` - stable branch
- `develop` - mainstream branch for development, we merge new features into it
- `feature/new_cool_feature` - for adding every new functionality please use a separate branch. We will merge it into develop branch after pull request.

## Knowledge base

There are collected useful suitable articles and code examples, which were partially used for create current solution:

- [Multiprocessing vs. Threading in Python: What you need to know](https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/)

- [example from multiprocessing Pool and KeyboardInterrupt handling](https://github.com/jreese/multiprocessing-keyboardinterrupt)

- [aiven-examples](https://github.com/aiven/aiven-examples)

  

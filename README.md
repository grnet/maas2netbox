[![Build Status](https://travis-ci.com/grnet/maas2netbox.svg?branch=master)](https://travis-ci.com/grnet/maas2netbox)
[![codecov](https://codecov.io/gh/grnet/maas2netbox/branch/master/graph/badge.svg)](https://codecov.io/gh/grnet/maas2netbox)

# MaaS2Netbox
MaaS2Netbox is a project which aims to update an existing NetBox database of a Node inventory with information gathered
by MaaS for the same set of Nodes.

## Requirements
In order to run MaaS2Netbox scripts the following requirements must be met:

1. API read access to desired MaaS deployment
2. API read access to desired NetBox deployment
3. (optional) API write access to desired NetBox deployment in order to update the information stored in NetBox

## Docker
```bash
cd docker
docker build -t maas2netbox .
cp env.list.sampleenv.list
# Edit docker/env.list with values of your choice

# Run maas2netbox with --help option to display all available options
docker run --env-file env.list maas2netbox maas2netbox --help
```

## Virtualenv
```bash
# Create Virtual Environment and install maas2netbox
virtualenv .venv -p python3
source .venv/bin/activate
pip install git+git://github.com/grnet/maas2netbox.git@master

# Export environment variables to configure maas2netbox
export MAAS_URL=https://maas.url
export MAAS_API_KEY='123AB:CDEF:1234'
export NETBOX_URL='https://netbox.url'
export NETBOX_TOKEN='0123456789ABCDEF'
export NETBOX_DEVICE_IDS=123,456
export SITE=dc_name

# Run maas2netbox with --help option to display all available options
maas2netbox --help
```

## Configuration Options with Environment Variables

| Name                | Description                                                           |
| ----                | -----------                                                           |
| `MAAS_URL`          | The Rest API url of MaaS Deployment                                   |
| `MAAS_API_KEY`      | The OATH API key for read transactions to MaaS Rest API endpoints     |
| `NETBOX_URL`        | The Rest API url of NetBox Deployment                                 |
| `NETBOX_TOKEN`      | The token for read/write transactions to NetBox API endpoints         |
| `NETBOX_DEVICE_IDS` | A list containing all device type ids of nodes inside NetBox database |
| `SITE`              | The name of the site whose machines are managed by MaaS               |

**NOTE:** All environment variables are mandatory and should be set appropriately.

## Usage
Usage: `maas2netbox [-h] -c COMMAND -f FIELD [--log LOG_LEVEL] [--data DATA]`

| Argument               | Valid Options                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------- |
| `COMMAND`              | `validate`, `update`, `create`                                                                          |
| `FIELD`                | `serialnumber`, `status`, `primaryIPv4`, `interfaces`, `platform`, `switch_connections`, `experimental` |
| `LOG_LEVEL` (optional) | `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET`                                               |
| `DATA` (optional)      | is a valid json dictionary                                                                              |

## Jenkins Job
MaaS2Netbox is accompanied with a Jenkins Job which can be added to any
Jenkins Environment. This job assumes that there is an agent named
maas2netbox-worker (changes can be easily applied) with all the
installation requirements met. In addition, there is a cron trigger
which runs the job in a daily basis. Finally, the Jenkins Job runs all
the validation scripts and it gathers the whole output from MaaS2Netbox
execution.

## Conventions
In order to run MaaS2Netbox scripts successfully the following
conventions must be made:

1. A node object in MaaS must have the same name in NetBox (case
insensitive)

## Limitations
At the moment, MaaS2Netbox support only Lenovo hardware nodes.

## Known Issues
The following issues have been recorded and they will be fixed in newer
versions of MaaS2Netbox:

* In order to check cabling of a node with a network switch, all switch
ports must be declared beforehand to NetBox

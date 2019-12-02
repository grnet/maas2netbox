[![Build Status](https://travis-ci.com/grnet/maas2netbox.svg?branch=master)](https://travis-ci.com/grnet/maas2netbox)
[![codecov](https://codecov.io/gh/grnet/maas2netbox/branch/master/graph/badge.svg)](https://codecov.io/gh/grnet/maas2netbox)

# MaaS2Netbox
MaaS2Netbox is a project which aims to update an existing
NetBox database of a Node inventory with information gathered by MaaS
for the same set of Nodes.

## Installation

### Requirements
In order to run MaaS2Netbox scripts the following requirements must be
met:

1. `docker` must be installed
2. `docker-compose` must be installed
3. Linux user must belong to either `docker` or `sudo` group
4. Connectivity with the IPMI network of hardware nodes must be ensured
4. API read access to desired MaaS deployment
5. API read access to desired NetBox deployment
6. (optional) API write access to desired NetBox deployment in order to
update the information stored in NetBox

### Setup
If all requirements are met, user can start the MaaS2Netbox container
with docker-compose by providing a config.yml file of the following
format:

```yaml
---
ipmi:
  username: user
  password: userpass
  dns_zone: mgmt.name.com
maas:
  url: https://maas.url
  api_key: '123AB:CDEF:1234'
netbox:
  url: 'https://netbox.url'
  token: '0123456789ABCDEF'
  device_ids:
    - 123
    - 456
site: dc_name
```

#### Parameters

| Name                | Description                                                           |
| ----                | -----------                                                           |
| IPMI `username`     | The username for IPMI access                                          |
| IPMI `password`     | The password for IPMI access                                          |
| MaaS `url`          | The Rest API url of MaaS Deployment                                   |
| MaaS `api_key`      | The OATH API key for read transactions to MaaS Rest API endpoints     |
| NetBox `url`        | The Rest API url of NetBox Deployment                                 |
| NetBox `token`      | The token for read/write transactions to NetBox API endpoints         |
| NetBox `device_ids` | A list containing all device type ids of nodes inside NetBox database |
| `site`              | The name of the site whose machines are managed by MaaS               |

**NOTE 1:** All fields are mandatory

**NOTE 2:** The config.yml should be placed at the same directory of
docker-compose.

## Usage

User can execute the MaaS2Netbox by a dedicated CLI inside Docker
container:

Usage: `maas2netbox [-h] -c COMMAND -f FIELD [--log LOG_LEVEL]
[--data DATA]`

| Argument             | Valid Options                                                                                                                                       |
| --------             | -------------                                                                                                                                       |
| `COMMAND`            | `validate`, `update`, `create`                                                                                                                      |
|`FIELD`               | `serialnumber`, `ipmi_location`, `ipmi_interface`, `status,primaryIPv4`, `interfaces`, `firmware`, `platform`, `switch_connections`, `experimental` |
|`LOG_LEVEL` (optional)| `CRITICAL`, `FATAL`, `ERROR`, `WARN`, `WARNING`, `INFO`, `DEBUG`, `NOTSET`                                                                          |
|`DATA` (optional)     | is a valid json dictionary                                                                                                                          |

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
2. A node object in NetBox must have the following custom fields:
    * `TSM`: This field contains the TSM firmware version
    * `BIOS`: This field contains the BIOS firmware version
    * `PSU`: This field contains the Power Supply Unit firmware version

## Limitations
At the moment, MaaS2Netbox support only Lenovo hardware nodes.

## Known Issues
The following issues have been recorded and they will be fixed in newer
versions of MaaS2Netbox:

* In order to check cabling of a node with a network switch, all switch
ports must be declared beforehand to NetBox

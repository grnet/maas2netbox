# Copyright (C) 2019  GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from maas.client import enum


maas_url = os.environ.get('MAAS_URL')
maas_api_key = os.environ.get('MAAS_API_KEY')
netbox_url = os.environ.get('NETBOX_URL')
netbox_token = os.environ.get('NETBOX_TOKEN')
try:
    netbox_device_ids = os.environ.get('NETBOX_DEVICE_IDS').split(',')
except AttributeError:
    netbox_device_ids = []
site_name = os.environ.get('SITE')

STATUS_DICT = {
    enum.NodeStatus.DEPLOYED: 'Active',
    enum.NodeStatus.ALLOCATED: 'Planned',
    enum.NodeStatus.NEW: 'Inventory',
    enum.NodeStatus.DEFAULT: 'Inventory',
    enum.NodeStatus.READY: 'Offline',
    enum.NodeStatus.BROKEN: 'Failed',
    enum.NodeStatus.FAILED_COMMISSIONING: 'Failed',
    enum.NodeStatus.FAILED_DEPLOYMENT: 'Failed',
    enum.NodeStatus.RESCUE_MODE: 'Failed',
    enum.NodeStatus.FAILED_TESTING: 'Failed',
    enum.NodeStatus.FAILED_EXITING_RESCUE_MODE: 'Failed',
    enum.NodeStatus.FAILED_ENTERING_RESCUE_MODE: 'Failed',
    enum.NodeStatus.FAILED_DISK_ERASING: 'Failed',
    enum.NodeStatus.FAILED_RELEASING: 'Failed',
    enum.NodeStatus.COMMISSIONING: None,
    enum.NodeStatus.DEPLOYING: None,
    enum.NodeStatus.ENTERING_RESCUE_MODE: None,
    enum.NodeStatus.EXITING_RESCUE_MODE: None,
    enum.NodeStatus.TESTING: None,
    enum.NodeStatus.RELEASING: None,
    enum.NodeStatus.DISK_ERASING: None,
    enum.NodeStatus.MISSING: 'Failed',
    enum.NodeStatus.RESERVED: 'Planned',
    enum.NodeStatus.RETIRED: 'Offline'
}

CABLE_COLORS = {
    'red': 'f44336',
    'pink': 'e91e63',
    'rose': 'ffe4e1',
    'fuschia': 'ff66ff',
    'purple': '9c27b0',
    'indigo': '3f51b5',
    'blue': '2196f3',
    'cyan': '00bcd4',
    'teal': '009688',
    'aqua': '00ffff',
    'green': '4caf50',
    'lime': 'cddc39',
    'yellow': 'ffeb3b',
    'amber': 'ffc107',
    'orange': 'ff9800',
    'brown': '795548',
    'grey': '9e9e9e',
    'black': '111111',
    'white': 'ffffff'
}

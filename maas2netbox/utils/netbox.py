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

import json
import logging
from urllib.error import URLError
import urllib.request

import pynetbox

from maas2netbox import config


def get_api_object():
    nb = pynetbox.api(
        config.netbox_url,
        token=config.netbox_token
    )
    return nb


def patch_resource(resource, url, data):
    req = urllib.request.Request(url, method='PATCH')
    req.add_header('Authorization', 'Token %s' % config.netbox_token)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Accept', 'application/json')
    jsondata = json.dumps(data)
    jsondataasbytes = jsondata.encode('utf-8')

    try:
        urllib.request.urlopen(req, jsondataasbytes).read()
    except URLError as e:
        logging.error('Failed to update {}'.format(resource))
        if hasattr(e, 'reason'):
            logging.error('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            logging.error('Error code: ', e.code)
        return False
    else:
        logging.info('{} updated successfully'.format(resource))
        return True


def create_resource(resource, url, data):
    req = urllib.request.Request(url, method='POST')
    req.add_header('Authorization', 'Token %s' % config.netbox_token)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Accept', 'application/json')
    jsondata = json.dumps(data)
    jsondataasbytes = jsondata.encode('utf-8')

    try:
        ret = urllib.request.urlopen(req, jsondataasbytes).read()
    except URLError as e:
        logging.error('Failed to create {}'.format(resource))
        if hasattr(e, 'reason'):
            logging.error('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            logging.error('Error code: ', e.code)
        return None
    else:
        logging.info('{} created successfully'.format(resource))
        return json.loads(ret.decode('utf-8'))['id']


def get_nodes(nb):
    return nb.dcim.devices.filter(
        site=config.site_name, device_type_id=config.netbox_device_ids)


def get_node_by_name(nb, name):
    return nb.dcim.devices.get(name=name)


def get_node(nb, node_id):
    return nb.dcim.devices.get(node_id)


def get_node_interface(nb, interface_id):
    return nb.dcim.interfaces.get(name=interface_id)


def get_node_interfaces(nb, node_id, name=None):
    if name:
        return nb.dcim.interfaces.filter(device_id=node_id, name=name)
    else:
        return nb.dcim.interfaces.filter(device_id=node_id)


def get_node_platforms(nb):
    return nb.dcim.platforms.all()


def get_node_statuses(nb):
    return nb.dcim.choices()['device:status']


def get_interface_types(nb):
    return nb.dcim.choices()['interface:type']


def get_node_ipmi_interface(nb, node_id):
    ifaces = get_node_interfaces(nb, node_id)
    ipmi_interface = None
    for iface in ifaces:
        if iface['mgmt_only']:
            ipmi_interface = iface
            break
    return ipmi_interface


def get_vlan_id(nb, vid):
    return nb.ipam.vlans.filter(site=config.site_name, vid=vid)


def get_ip_address(nb, address):
    results = nb.ipam.ip_addresses.filter(address=address)
    if len(results) == 1:
        return results[0]


def get_cable(nb, node_iface, switch_iface):
    cables = nb.dcim.cables.filter(site=config.site_name)
    for cable in cables:
        if (
            cable['termination_a_id'] == node_iface
            and cable['termination_b_id'] == switch_iface
        ):
            return cable


def patch_interface(interface_id, data):
    url = ('{}/dcim/interfaces/{}/'.format(config.netbox_url, interface_id))
    return patch_resource('Interface', url, data)


def patch_node(node_id, data):
    url = ('{}/dcim/devices/{}/'.format(config.netbox_url, node_id))
    return patch_resource('Node', url, data)


def create_interface(data):
    url = ('{}/dcim/interfaces/'.format(config.netbox_url))
    return create_resource('Interface', url, data)


def create_ip_address(data):
    url = ('{}/ipam/ip-addresses/'.format(config.netbox_url))
    return create_resource('IP Address', url, data)


def create_cable(data):
    url = ('{}/dcim/cables/'.format(config.netbox_url))
    return create_resource('Cable', url, data)

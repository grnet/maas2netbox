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

from maas2netbox import config

import json
import logging
from urllib.error import URLError
import urllib.request


def get_resource(url):
    req = urllib.request.Request(url)
    req.add_header('Authorization', 'Token %s' % config.netbox_token)
    res = urllib.request.urlopen(req).read()
    return json.loads(res.decode('utf-8'))


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


def get_nodes_by_site(site):
    device_ids = ''
    for device_id in config.netbox_device_ids:
        device_ids += '&device_type_id={}'.format(device_id)
    url = (
        '{}/dcim/devices/?site={}{}&limit=0'.format(
            config.netbox_url, site, device_ids))
    return get_resource(url)['results']


def get_node_by_name(name):
    url = ('{}/dcim/devices/?name={}'.format(config.netbox_url, name))
    return get_resource(url)['results'][0]


def get_node(node_id):
    url = ('{}/dcim/devices/{}'.format(config.netbox_url, node_id))
    return get_resource(url)


def get_node_interface(interface_id):
    url = ('{}/dcim/interfaces/{}'.format(config.netbox_url, interface_id))
    return get_resource(url)


def get_node_interfaces(node_id, name=None):
    url = (
        '{}/dcim/interfaces/?device_id={}'.format(
            config.netbox_url, node_id))
    if name:
        url += '&name={}'.format(name)
    return get_resource(url)['results']


def get_node_platforms():
    url = ('{}/dcim/platforms/'.format(config.netbox_url))
    return get_resource(url)['results']


def get_node_statuses():
    url = ('{}/dcim/_choices/device:status/'.format(config.netbox_url))
    return get_resource(url)


def get_form_factors():
    url = ('{}/dcim/_choices/interface:form_factor/'.format(config.netbox_url))
    return get_resource(url)


def get_node_ipmi_interface(node):
    ifaces = get_node_interfaces(node['id'])
    ipmi_interface = None
    for iface in ifaces:
        if iface['mgmt_only']:
            ipmi_interface = iface
            break
    return ipmi_interface


def get_vlan_id_of_site(site, vid):
    url = (
        '{}/ipam/vlans/?site={}&vid={}'.format(config.netbox_url, site, vid))
    return get_resource(url)['results'][0]['id']


def get_ip_address(address):
    url = (
        '{}/ipam/ip-addresses/?address={}'.format(config.netbox_url, address))
    results = get_resource(url)['results']
    if len(results) == 1:
        return results[0]
    else:
        return None


def get_cable(node_iface, switch_iface):
    url = '{}/dcim/cables/?limit=0'.format(config.netbox_url)
    cables = get_resource(url)['results']
    for cable in cables:
        if (
            cable['termination_a_id'] == node_iface
            and cable['termination_b_id'] == switch_iface
        ):
            return cable
    return None


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

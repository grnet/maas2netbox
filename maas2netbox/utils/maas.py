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

import re
from xml.etree import ElementTree

from maas import client

from maas2netbox import config


def get_nodes():
    cli = client.connect(config.maas_url, apikey=config.maas_api_key)
    nodes = cli.machines.list()

    return nodes


def get_node_serial(node):
    serial = None
    try:
        node_details = node.get_details()['lshw']
        tree = ElementTree.fromstring(node_details)
        serial = tree.findall("./node[@class='system']/serial")[0].text
    except (KeyError, AttributeError, IndexError, ElementTree.ParseError):
        pass

    return serial


def get_interface_ipv4_address(iface):
    address = None
    try:
        address = iface.links[0].ip_address
        mask = iface.links[0].subnet.cidr.split('/')[-1]
        if address and mask:
            address = '{}/{}'.format(address, mask)
    except (IndexError, AttributeError):
        pass

    return address


def get_node_interfaces(node):
    ifaces = []
    try:
        node_details = node.get_details()['lshw']
        tree = ElementTree.fromstring(node_details)
        ifaces_objects = tree.findall(
            "node[@class='system']/node[@class='bus']/"
            "node[@class='bridge']/node[@class='bridge']/"
            "node[@class='network']")
        for ifaces_object in ifaces_objects:
            iface = {}
            for iface_property in ifaces_object.iter():
                if iface_property.tag == 'serial':
                    iface['mac_address'] = iface_property.text.upper()
                elif iface_property.tag == 'logicalname':
                    iface['name'] = iface_property.text
                elif iface_property.tag == 'configuration':
                    for conf_property in iface_property.getchildren():
                        if conf_property.attrib['id'] == 'driver':
                            if conf_property.attrib['value'] == 'igb':
                                iface['type'] = '1000'
                            elif conf_property.attrib['value'] == 'ixgbe':
                                iface['type'] = '1150'
            ifaces.append(iface)
    except (KeyError, IndexError, AttributeError, ElementTree.ParseError):
        pass

    return ifaces


def calculate_color(text):
    color = None
    try:
        color_name = re.findall(r'\(.*port: (\w+)\)', text)[0]
        color = config.CABLE_COLORS[color_name]
    except (KeyError, IndexError):
        pass

    return color


def get_switch_connection_details(node):
    ifaces = []
    try:
        node_details = node.get_details()['lldp']
        tree = ElementTree.fromstring(node_details)
        ifaces_objects = tree.findall('interface')
        for iface_object in ifaces_objects:
            iface = {
                'name': iface_object.attrib['name'],
                'switch_name': iface_object.find('chassis/name').text,
                'switch_port': iface_object.find('port/id').text,
                'vid': iface_object.find('vlan').attrib['vlan-id'],
                'cable_color': calculate_color(
                    iface_object.find('port/descr').text)
            }
            ifaces.append(iface)
    except (KeyError, AttributeError, ElementTree.ParseError):
        pass

    return ifaces

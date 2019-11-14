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

from maas.client import enum

from maas2netbox.utils import maas, netbox


class Creator(object):
    def __init__(self, data):
        self.netbox_api = netbox.NetBoxAPI()
        if data:
            self.data = json.loads(data)

    @property
    def netbox_nodes(self):
        nodes = self.netbox_api.get_nodes()
        node_dict = {}
        for node in nodes:
            node_dict[node.name.lower()] = node.id
        return node_dict

    @property
    def maas_nodes(self):
        nodes = []
        maas_nodes = maas.get_nodes()
        for node in maas_nodes:
            if (
                node.status in [
                    enum.NodeStatus.DEPLOYED, enum.NodeStatus.READY]
            ):
                nodes.append(node)
        return nodes

    def create(self):
        raise NotImplementedError


class IPMIInterfaceCreator(Creator):

    def get_interface_type_value(self, interface_type_text):
        interface_type_value = None
        interface_types = self.netbox_api.get_interface_types()
        for interface_type in interface_types:
            if interface_type['label'] == interface_type_text:
                interface_type_value = interface_type['value']
                break
        return interface_type_value

    def create(self):
        interface_data = {
            'name': ''.join(self.data['mac_address'].split(':')),
            'type': self.get_interface_type_value(
                self.data['type']),
            'device': self.data['node'],
            'enabled': True,
            'mtu': 1500,
            'mac_address': self.data['mac_address'],
            'mgmt_only': True,
            'mode': 100
        }
        self.netbox_api.create_interface(interface_data)


class VirtualInterfacesCreator(Creator):

    def get_iface_data(self, iface, node_id):
        iface_data = {
            'device': node_id,
            'name': iface.name,
            'enabled': iface.enabled,
            'mac_address': iface.mac_address,
            'mtu': iface.effective_mtu
        }

        if iface.vlan and iface.vlan.vid != 0:
            iface_data['mode'] = 200
            vlan = self.netbox_api.get_vlan_id(iface.vlan.vid)
            iface_data['tagged_vlans'] = [vlan]
        else:
            iface_data['mode'] = 100

        if iface.type == enum.InterfaceType.BOND:
            iface_data['type'] = 200
        elif iface.type == enum.InterfaceType.VLAN:
            iface_data['type'] = 32767
        elif iface.type == enum.InterfaceType.BRIDGE:
            iface_data['type'] = 32767

        return iface_data

    def get_netbox_node_ifaces_dict(self, node_id):
        node_ifaces = self.netbox_api.get_node_interfaces(node_id)
        ifaces_dict = {}
        for iface in node_ifaces:
            ifaces_dict[iface.name] = iface.id
        return ifaces_dict

    def create_interfaces(self, maas_node, netbox_node, netbox_node_ifaces):
        for iface in maas_node.interfaces:
            if iface.type != enum.InterfaceType.UNKNOWN:
                if iface.name not in netbox_node_ifaces:
                    iface_data = self.get_iface_data(iface, netbox_node)
                    netbox_iface_id = self.netbox_api.create_interface(
                        iface_data)
                    netbox_node_ifaces[iface.name] = netbox_iface_id

    def patch_parent_interfaces(self, maas_node, netbox_node_ifaces):
        for iface in maas_node.interfaces:
            if iface.type != enum.InterfaceType.UNKNOWN:
                netbox_iface_id = netbox_node_ifaces[iface.name]
                for iface_parent in iface.parents:
                    netbox_parent_iface = netbox_node_ifaces[iface_parent.name]
                    if iface.type == enum.InterfaceType.BOND:
                        self.netbox_api.patch_interface(
                            netbox_parent_iface, {'lag': netbox_iface_id})
                    elif iface.type == enum.InterfaceType.VLAN:
                        self.netbox_api.patch_interface(
                            netbox_iface_id, {'lag': netbox_parent_iface})
                    elif iface.type == enum.InterfaceType.BRIDGE:
                        self.netbox_api.patch_interface(
                            netbox_iface_id, {'lag': netbox_parent_iface})

    def create_ip_addresses(self, maas_node, netbox_node, netbox_node_ifaces):
        for iface in maas_node.interfaces:
            ipv4 = maas.get_interface_ipv4_address(iface)
            if ipv4:
                netbox_iface_id = netbox_node_ifaces[iface.name]
                ip_data = {
                    "address": ipv4,
                    "status": 1,
                    "interface": netbox_iface_id,
                }
                if not self.netbox_api.get_ip_address(ipv4):
                    address_id = self.netbox_api.create_ip_address(ip_data)
                    if address_id and iface.vlan.vid == 0:
                        self.netbox_api.patch_node(
                            netbox_node, {'primary_ip4': address_id})

    def update_physical_interfaces(self, maas_node, netbox_node_ifaces):
        for iface in maas_node.interfaces:
            if iface.type == enum.InterfaceType.PHYSICAL:
                iface_data = {
                    'mtu': iface.effective_mtu
                }
                if iface.vlan and iface.vlan.vid != 0:
                    iface_data['mode'] = 200
                    vlan = self.netbox_api.get_vlan_id(iface.vlan.vid)
                    iface_data['tagged_vlans'] = [vlan]
                else:
                    iface_data['mode'] = 100
                netbox_iface_id = netbox_node_ifaces[iface.name]
                self.netbox_api.patch_interface(netbox_iface_id, iface_data)

    @staticmethod
    def get_cable_data(iface, switch_port, color):
        data = {
            "termination_a_type": "dcim.interface",
            "termination_b_type": "dcim.interface",
            "status": True,
            "termination_a_id": iface,
            "termination_b_id": switch_port,
        }
        if color:
            data['color'] = color
        return data

    def create_switch_connections(self, maas_node, netbox_node_ifaces):
        ifaces_details = maas.get_switch_connection_details(maas_node)
        for iface in ifaces_details:
            netbox_iface_id = netbox_node_ifaces[iface['name']]
            netbox_iface = self.netbox_api.get_node_interface(netbox_iface_id)
            data = {
                'untagged_vlan': self.netbox_api.get_vlan_id(iface['vid'])
            }
            self.netbox_api.patch_interface(netbox_iface_id, data)
            if netbox_iface.lag:
                self.netbox_api.patch_interface(
                    netbox_iface.lag.id, data)

            switch = self.netbox_api.get_node_by_name(iface['switch_name'])
            switch_port = self.netbox_api.get_node_interfaces(
                switch.id, iface['switch_port'])[0]
            if not self.netbox_api.get_cable(
                    netbox_iface_id, switch_port.id):
                cable_data = self.get_cable_data(
                    netbox_iface_id, switch_port.id, iface['cable_color'])
                self.netbox_api.create_cable(cable_data)

    def create(self):
        for maas_node in self.maas_nodes:
            try:
                netbox_node = self.netbox_nodes[maas_node.hostname]
            except KeyError:
                continue

            logging.info(
                'Updating Node: {}...'.format(
                    maas_node.hostname.upper()))

            netbox_node_ifaces = self.get_netbox_node_ifaces_dict(netbox_node)

            # create interface if not present
            self.create_interfaces(maas_node, netbox_node, netbox_node_ifaces)

            # update physical interfaces
            self.update_physical_interfaces(maas_node, netbox_node_ifaces)

            # patch parent interfaces to let them know they are part of this
            # LAG
            self.patch_parent_interfaces(maas_node, netbox_node_ifaces)

            # Create IP addresses of all interfaces of the node
            self.create_ip_addresses(
                maas_node, netbox_node, netbox_node_ifaces)

            # Create Switch Connections
            self.create_switch_connections(maas_node, netbox_node_ifaces)

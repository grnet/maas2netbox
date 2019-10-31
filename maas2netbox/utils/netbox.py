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

import pynetbox

from maas2netbox import config


class NetBoxAPI(object):
    def __init__(self):
        self.api = pynetbox.api(
            config.netbox_url,
            token=config.netbox_token
        )

    def get_nodes(self):
        return self.api.dcim.devices.filter(
            site=config.site_name, device_type_id=config.netbox_device_ids)

    def get_node_by_name(self, name):
        return self.api.dcim.devices.get(name=name)

    def get_node(self, node_id):
        return self.api.dcim.devices.get(node_id)

    def get_node_interface(self, interface_id):
        return self.api.dcim.interfaces.get(name=interface_id)

    def get_node_interfaces(self, node_id, name=''):
        if name:
            return self.api.dcim.interfaces.filter(
                device_id=node_id, name=name)
        else:
            return self.api.dcim.interfaces.filter(device_id=node_id)

    def get_node_platforms(self):
        return self.api.dcim.platforms.all()

    def get_node_statuses(self):
        return self.api.dcim.choices()['device:status']

    def get_interface_types(self):
        return self.api.dcim.choices()['interface:type']

    def get_node_ipmi_interface(self, node_id):
        ifaces = self.get_node_interfaces(node_id)
        ipmi_interface = None
        for iface in ifaces:
            if iface.mgmt_only:
                ipmi_interface = iface
                break
        return ipmi_interface

    def get_vlan_id(self, vid):
        return self.api.ipam.vlans.filter(site=config.site_name, vid=vid)

    def get_ip_address(self, address):
        results = self.api.ipam.ip_addresses.filter(address=address)
        if len(results) == 1:
            return results[0]
        else:
            return None

    def get_cable(self, node_iface, switch_iface):
        cables = self.api.dcim.cables.filter(site=config.site_name)
        for cable in cables:
            if (
                cable.termination_a_id == node_iface
                and cable.termination_b_id == switch_iface
            ):
                return cable
        return None

    def patch_interface(self, interface_id, data):
        iface = self.api.dcim.interfaces.get(interface_id)
        return iface.update(data)

    def patch_node(self, node_id, data):
        node = self.api.dcim.devices.get(node_id)
        return node.update(data)

    def create_interface(self, data):
        return self.api.dcim.interfaces.create(data).id

    def create_ip_address(self, data):
        return self.api.ipam.ip_addresses.create(data).id

    def create_cable(self, data):
        return self.api.dcim.cables.create(data).id

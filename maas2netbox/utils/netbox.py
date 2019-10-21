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


def get_api_object():
    nb = pynetbox.api(
        config.netbox_url,
        token=config.netbox_token
    )
    return nb


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


def patch_interface(nb, interface_id, data):
    iface = nb.dcim.interfaces.get(interface_id)
    return iface.update(data)


def patch_node(nb, node_id, data):
    node = nb.dcim.devices.get(node_id)
    return node.update(data)


def create_interface(nb, data):
    return nb.dcim.interfaces.create(data).id


def create_ip_address(nb, data):
    return nb.ipam.ip_addresses.create(data).id


def create_cable(nb, data):
    return nb.dcim.cables.create(data).id

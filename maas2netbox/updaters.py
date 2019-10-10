# Copyright (C) 2019  Stamatis Katsaounis <skatsaounis@admin.grnet.gr>
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

from maas2netbox.utils import netbox


class Updater(object):
    def __init__(self, nodes_updates):
        self.nodes_updates = nodes_updates

    @staticmethod
    def get_node_custom_fields(node_id):
        node = netbox.get_node(node_id)
        return node['custom_fields']

    def update_nodes(self):
        raise NotImplementedError()


class SerialNumberUpdater(Updater):

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            netbox.patch_node(node_id, {'serial': value['expected']})


class IPMIFieldUpdater(Updater):

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            custom_fields = self.get_node_custom_fields(node_id)
            custom_fields['IPMI'] = value['expected']
            netbox.patch_node(node_id, {'custom_fields': custom_fields})


class IPMIInterfaceUpdater(Updater):

    def update_nodes(self):
        for interface_id, value in self.nodes_updates.items():
            netbox.patch_interface(
                interface_id, {
                    'name': ''.join(value['expected'].split(':')),
                    'mac_address': value['expected']})


class StatusUpdater(Updater):

    @staticmethod
    def get_status_value(status_text):
        status_value = None
        statuses = netbox.get_node_statuses()
        for status in statuses:
            if status['label'] == status_text:
                status_value = status['value']
        return status_value

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            status_value = self.get_status_value(value['expected'])
            netbox.patch_node(node_id, {'status': status_value})


class PrimaryIPv4Updater(Updater):

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            netbox.patch_node(node_id, {'primary_ip4': value['expected']})


class InterfacesUpdater(Updater):

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            for interface in value['expected']:
                interface['device'] = node_id
                netbox.create_interface(interface)


class FirmwareUpdater(Updater):

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            custom_fields = self.get_node_custom_fields(node_id)
            for firmware, version in value['expected'].items():
                custom_fields[firmware] = version
            netbox.patch_node(node_id, {'custom_fields': custom_fields})


class PlatformUpdater(Updater):

    @staticmethod
    def get_platform_id(value):
        platform_id = None
        platforms = netbox.get_node_platforms()
        for platform in platforms:
            if platform['slug'] == value:
                platform_id = platform['id']
                break
        return platform_id

    def update_nodes(self):
        for node_id, value in self.nodes_updates.items():
            netbox.patch_node(
                node_id, {'platform': self.get_platform_id(value['expected'])})


class ExperimentalUpdater(Updater):

    def update_nodes(self):
        super(ExperimentalUpdater, self).update_nodes()

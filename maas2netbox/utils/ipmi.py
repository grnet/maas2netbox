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

import subprocess


def get_mac_address(ipv4, username, password):
    cmd = [
        "/bin/bash",
        "-c",
        "ipmitool -I lanplus -H {} -U {} -P {} lan print |"
        " grep 'MAC Address' | awk '{{print $4}}'"
        .format(ipv4, username, password)]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    return outs[:-1]


def get_firmware_versions(ipv4, username, password):
    cmd = [
        "/bin/bash",
        "-c",
        "/opt/lenovo/osput/osput -c getServerInfo -u {} -p {} -H {}"
        .format(username, password, ipv4)]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    return outs[:-1]


def parse_firmware_versions(output):
    """ Returns a dictionary with the firmware version of BIOS, TSM and PSU
    hardware components of a Lenovo Server

    Sample OSCLI Output:
    ...
    Server components:

    Device type: BIOS
    Device id: LG_BIOS_000
    Slot number: 0
    Device status: Device present
    Current version: 4.86.0

    Device type: System Manager
    Device id: LG_TSM
    Slot number: 0
    Device status: Device present
    Current version: 4.83.396

    Device type: PSU
    Device id: PS_0201
    Slot number: 1
    Device status: Device present
    Current version: 3.31.0

    Device type: PSU
    Device id: PS_0201
    Slot number: 2
    Device status: Device present
    Current version: 3.31.0

    Expected return value:
    {
        'BIOS': '4.86.0',
        'TSM': '4.83.396',
        'PSU': '1/PS_0201: 3.31.0, 2/PS_0201: 3.31.0',
    }

    """
    try:
        firmware_info = output.decode().split(
            'Server components:\n\n')[1].split('\n')
    except IndexError:
        return {}

    firmware_assets = [
        firmware_info[x:x + 5] for x in range(
            0, len(firmware_info), 6) if any(
                firmware in firmware_info[x] for firmware in [
                    'BIOS', 'PSU', 'System Manager'])]
    firmware_dict = [dict(map(lambda x: x.split(': '), y)) for y in
                     firmware_assets]
    bios = next(i for i in firmware_dict if i['Device type'] == 'BIOS' and i[
        'Device status'] == 'Device present')
    tsm = next(i for i in firmware_dict if
               i['Device type'] == 'System Manager' and i[
                   'Device status'] == 'Device present')
    psus = [i for i in firmware_dict if i['Device type'] == 'PSU']
    psu_value = ', '.join(['{}/{}: {}'.format(x['Slot number'], x['Device id'],
                                              x['Current version']) for x in
                           psus if x['Device status'] == 'Device present'])
    firmware_versions = {
        'BIOS': bios['Current version'],
        'TSM': tsm['Current version'],
        'PSU': psu_value
    }

    return firmware_versions

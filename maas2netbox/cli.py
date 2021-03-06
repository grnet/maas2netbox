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

import argparse
import logging

from maas2netbox import validators, updaters, creators


def run_validation(args):
    validator = None
    if args.field == 'serialnumber':
        validator = validators.SerialNumberValidator(use_maas=True)
    elif args.field == 'status':
        validator = validators.StatusValidator(use_maas=True)
    elif args.field == 'primaryIPv4':
        validator = validators.PrimaryIPv4Validator(use_maas=True)
    elif args.field == 'interfaces':
        validator = validators.InterfacesValidator(use_maas=True)
    elif args.field == 'platform':
        validator = validators.PlatformValidator(use_maas=True)
    elif args.field == 'switch_connections':
        validator = validators.SwitchConnectionsValidator(use_maas=True)
    elif args.field == 'experimental':
        validator = validators.ExperimentalValidator(use_maas=True)

    return validator.check_nodes()


def run_updates(args):
    nodes_with_errors = run_validation(args)

    updater = None
    if args.field == 'serialnumber':
        updater = updaters.SerialNumberUpdater(nodes_with_errors)
    elif args.field == 'status':
        updater = updaters.StatusUpdater(nodes_with_errors)
    elif args.field == 'primaryIPv4':
        updater = updaters.PrimaryIPv4Updater(nodes_with_errors)
    elif args.field == 'interfaces':
        updater = updaters.InterfacesUpdater(nodes_with_errors)
    elif args.field == 'platform':
        updater = updaters.PlatformUpdater(nodes_with_errors)
    elif args.field == 'experimental':
        updater = updaters.ExperimentalUpdater(nodes_with_errors)

    return updater.update_nodes()


def run_creators(args):
    if args.field == 'experimental':
        creator = creators.VirtualInterfacesCreator(args.data)
    else:
        raise NotImplementedError

    return creator.create()


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Helper Scripts to update NetBox Information from MaaS'),
        epilog=(
            'MaaS2Netbox usage: maas2netbox -c <command> -f <field>'),
    )
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument(
        '-c', dest='command', help='Choose command',
        choices=['validate', 'update', 'create'], required=True)
    required_args.add_argument(
        '-f', dest='field', help='Choose field',
        choices=['serialnumber', 'status', 'primaryIPv4', 'interfaces',
                 'platform', 'switch_connections', 'experimental'],
        required=True)
    parser.add_argument(
        '--log', dest='loglevel',
        choices=['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO',
                 'DEBUG', 'NOTSET'], default='INFO')
    parser.add_argument(
        '--data', dest='data', help='JSON data in string format',
        required=False)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    if args.command == 'validate':
        run_validation(args)
    elif args.command == 'update':
        run_updates(args)
    elif args.command == 'create':
        run_creators(args)


if __name__ == '__main__':
    main()

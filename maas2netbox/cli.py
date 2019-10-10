#!/usr/bin/env python3.6
import argparse
import logging

from maas2netbox import config
from maas2netbox.utils import maas, netbox
from maas2netbox import validators, updaters, creators


def run_validation(args):
    netbox_nodes = netbox.get_nodes_by_site(config.site)
    maas_nodes = maas.get_nodes()

    validator = None
    if args.field == 'serialnumber':
        validator = validators.SerialNumberValidator(netbox_nodes, maas_nodes)
    elif args.field == 'ipmi_location':
        validator = validators.IPMIFieldValidator(netbox_nodes, None)
    elif args.field == 'ipmi_interface':
        validator = validators.IPMIInterfaceValidator(netbox_nodes, None)
    elif args.field == 'status':
        validator = validators.StatusValidator(netbox_nodes, maas_nodes)
    elif args.field == 'primaryIPv4':
        validator = validators.PrimaryIPv4Validator(netbox_nodes, maas_nodes)
    elif args.field == 'interfaces':
        validator = validators.InterfacesValidator(netbox_nodes, maas_nodes)
    elif args.field == 'firmware':
        validator = validators.FirmwareValidator(netbox_nodes, None)
    elif args.field == 'platform':
        validator = validators.PlatformValidator(netbox_nodes, maas_nodes)
    elif args.field == 'switch_connections':
        validator = validators.SwitchConnectionsValidator(
            netbox_nodes, maas_nodes)
    elif args.field == 'experimental':
        validator = validators.ExperimentalValidator(netbox_nodes, maas_nodes)

    return validator.check_nodes()


def run_updates(args):
    nodes_with_errors = run_validation(args)

    updater = None
    if args.field == 'serialnumber':
        updater = updaters.SerialNumberUpdater(nodes_with_errors)
    elif args.field == 'ipmi_location':
        updater = updaters.IPMIFieldUpdater(nodes_with_errors)
    elif args.field == 'ipmi_interface':
        updater = updaters.IPMIInterfaceUpdater(nodes_with_errors)
    elif args.field == 'status':
        updater = updaters.StatusUpdater(nodes_with_errors)
    elif args.field == 'primaryIPv4':
        updater = updaters.PrimaryIPv4Updater(nodes_with_errors)
    elif args.field == 'interfaces':
        updater = updaters.InterfacesUpdater(nodes_with_errors)
    elif args.field == 'firmware':
        updater = updaters.FirmwareUpdater(nodes_with_errors)
    elif args.field == 'platform':
        updater = updaters.PlatformUpdater(nodes_with_errors)
    elif args.field == 'experimental':
        updater = updaters.ExperimentalUpdater(nodes_with_errors)

    return updater.update_nodes()


def run_creators(args):
    if args.field == 'ipmi_interface':
        creator = creators.IPMIInterfaceCreator(args.data)
    elif args.field == 'experimental':
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
        choices=['serialnumber', 'ipmi_location', 'ipmi_interface',
                 'status', 'primaryIPv4', 'interfaces', 'firmware',
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

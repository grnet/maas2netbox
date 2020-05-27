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

import unittest

from mock import patch, Mock


class CliTesting(unittest.TestCase):

    def setUp(self):
        modules = {
            'maas2netbox.config': Mock(),
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from maas2netbox import cli
        self.m2n_cli = cli

    def tearDown(self):
        self.module_patcher.stop()

    @patch('maas2netbox.cli.validators')
    def test_run_validation(self, mock_validators):
        serial_number_validator = Mock()
        mock_validators.SerialNumberValidator.return_value = \
            serial_number_validator
        check_result = Mock()
        serial_number_validator.check_nodes.return_value = check_result

        args = Mock()
        args.field = 'serialnumber'
        result = self.m2n_cli.run_validation(args)

        self.assertEqual(check_result, result)

    @patch('maas2netbox.cli.updaters')
    @patch('maas2netbox.cli.validators')
    def test_run_updates(self, mock_validators, mock_updaters):
        serial_number_validator = Mock()
        mock_validators.SerialNumberValidator.return_value = \
            serial_number_validator
        check_result = Mock()
        serial_number_validator.check_nodes.return_value = check_result

        serial_number_updater = Mock()
        mock_updaters.SerialNumberUpdater.return_value = \
            serial_number_updater
        update_result = Mock()
        serial_number_updater.update_nodes.return_value = update_result

        args = Mock()
        args.field = 'serialnumber'
        result = self.m2n_cli.run_updates(args)

        mock_updaters.SerialNumberUpdater.assert_called_once_with(check_result)
        self.assertEqual(update_result, result)

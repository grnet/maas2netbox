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

    @patch('maas2netbox.cli.creators')
    def test_run_creators(self, mock_creators):
        ipmi_interface_creator = Mock()
        mock_creators.IPMIInterfaceCreator.return_value = \
            ipmi_interface_creator
        create_result = Mock()
        ipmi_interface_creator.create.return_value = create_result

        args = Mock()
        args.field = 'ipmi_interface'
        result = self.m2n_cli.run_creators(args)

        mock_creators.IPMIInterfaceCreator.assert_called_once_with(args.data)
        self.assertEqual(create_result, result)

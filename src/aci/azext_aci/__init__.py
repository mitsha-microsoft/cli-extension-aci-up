# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_aci._help import helps  # pylint: disable=unused-import


class AciCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_aci._client_factory import cf_aci
        aci_custom = CliCommandType(
            operations_tmpl='azext_aci.custom#{}',
            client_factory=cf_aci)
        super(AciCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=aci_custom)

    def load_command_table(self, args):
        from azext_aci.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_aci._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AciCommandsLoader

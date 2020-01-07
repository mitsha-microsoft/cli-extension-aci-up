# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_aci._client_factory import cf_aci


def load_command_table(self, _):

    # TODO: Add command type here
    # aci_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_aci)


    with self.command_group('aci') as g:
        g.custom_command('create', 'create_aci')
        g.custom_command('up', 'aci_up')
        g.custom_command('list', 'list_aci')


    with self.command_group('aci', is_preview=True):
        pass


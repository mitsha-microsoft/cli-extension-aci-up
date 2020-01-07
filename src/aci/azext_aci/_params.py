# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    aci_name_type = CLIArgumentType(options_list='--aci-name-name', help='Name of the Aci.', id_part='name')
    code_link = CLIArgumentType(options_list='--code', help='Link to Code Repository (Empty if Current Working Directory Contains the Code)', id_part='code')
    port_number = CLIArgumentType(options_list='--port', help='Port on which your application runs (Default is 8080)', id_part='port')
    secrets_option = CLIArgumentType(options_list='--skip-secrets-generation', help='Set to True if have stored AZURE_CREDENTIALS Secrets in your Repository', id_part='skip_secrets_generation')
    wait_option = CLIArgumentType(options_list='--do-not-wait', hepl='Set to true if you don\'t want to wait for the Actions Workflow to end', id_part='do_not_wait')

    with self.argument_context('aci') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('aci_name', aci_name_type, options_list=['--name', '-n'])

    with self.argument_context('aci list') as c:
        c.argument('aci_name', aci_name_type, id_part=None)

    with self.argument_context('aci up') as c:
        c.argument('code', code_link, options_list=['--code'])
        c.argument('port', port_number, options_list=['--port'])
        c.argument('skip_secrets_generation', secrets_option, options_list=['--skip-secrets-generation'])
        c.argument('do_not_wait', wait_option, options_list=['--do-not-wait'])

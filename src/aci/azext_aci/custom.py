# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_aci(cmd, resource_group_name, aci_name, location=None, tags=None):
    raise CLIError('TODO: Implement `aci create`')


def list_aci(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `aci list`')


def update_aci(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance
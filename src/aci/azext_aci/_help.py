# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['aci'] = """
    type: group
    short-summary: Commands to Deploy your Application Directly to Azure Container Instances using GitHub Actions.
"""

helps['aci up'] = """
    type: command
    short-summary: Use this with your code/repository link to Deploy your Code
"""

helps['aci create'] = """
    type: command
    short-summary: Create a Aci.
"""

helps['aci list'] = """
    type: command
    short-summary: List Acis.
"""

# helps['aci delete'] = """
#     type: command
#     short-summary: Delete a Aci.
# """

# helps['aci show'] = """
#     type: command
#     short-summary: Show details of a Aci.
# """

# helps['aci update'] = """
#     type: command
#     short-summary: Update a Aci.
# """

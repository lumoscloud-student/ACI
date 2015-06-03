#!/usr/bin/python

'''
Simplified by Wei Zixi (ziwei@cisco.com) from original ACItoolkit for UCSD use case.
All credit to original author.

################################################################################
#         _____                      _      ____ _                             #
#        |_   _|__ _ __   __ _ _ __ | |_   / ___| | ___  _ __   ___            #
#          | |/ _ \ '_ \ / _` | '_ \| __| | |   | |/ _ \| '_ \ / _ \           #
#          | |  __/ | | | (_| | | | | |_  | |___| | (_) | | | |  __/           #
#          |_|\___|_| |_|\__,_|_| |_|\__|  \____|_|\___/|_| |_|\___|           #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
'''

import ast
import sys
import json
import time
from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Tenant

# Decrypted and use credentials defined below
from credentials import *

# Disable https certificate warning
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# Hardcoded variable for Your UCSD POC Case
#from_apic = {
#    # Fill in with the APIC admin user id
#    'LOGIN': '',
#    # Fill in with the APIC admin password
#    'PASSWORD': '',
#    # Fill in with the APIC IP address
#    'URL': 'https://' + '',
#    # Tenant or application that to be copied
#}
#
#to_apic = {
#    # Fill in with the APIC admin user id
#    'LOGIN': '',
#    # Fill in with the APIC admin password
#    'PASSWORD': '',
#    # Fill in with the APIC IP address
#    'URL': 'https://' + '',
#    # Tenant or application that to be copied
#}

# Define JSON manipulation actions
action = {
    # when copy_json is True, json files related to the tenant or application
    # profile will be acquire from APIC and push to your github account.
    # when paste_json is True, json file on your github account will be pulled
    # and applied to your target APIC (to_apic).
    'copy_json': True,
    'paste_json': True
}

# Gather Tenant name from cli argument
from_tenant = str(sys.argv[1])
to_tenant = str(sys.argv[2])

# Define function to get all tenant configuration as JSON from APIC
def get_json_file_from_apic():

    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    def get_contract_json():
        existing_tenants = Tenant.get(session)
        for tenant in existing_tenants:
            if str(tenant) == to_tenant:
                print 'Tenant existed, task aborted.'
                sys.exit()
        class_query_url = '/api/node/class/fvTenant.json'
        ret = session.get(class_query_url)
        data = ret.json()['imdata']
        for ap in data:
            dn = ap['fvTenant']['attributes']['dn']
            tenant_name = dn.split('/')[1][3:]
            #class_query_url = '/api/mo/uni/tn-aci-toolkit-demo.json?query-target=subtree&rsp-subtree=full&rsp-subtree-include=audit-logs,no-scoped'
            ap_query_url = '/api/mo/uni/tn-%s.json?rsp-subtree=full&rsp-prop-include=config-only' % (tenant_name)
            ret = session.get(ap_query_url)
            if tenant_name == from_tenant:
                return ast.literal_eval(ret.text)['imdata'][0]

    json_file = get_contract_json()
    return json_file

# Define function to push JSON configuration to APIC
def push_json_to_apic(json_content):
    """
    :param json_content: the json file to be pushed to APIC
    :return: the respond of the push action
    """
    session = Session(to_apic['URL'], to_apic['LOGIN'], to_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    return session.push_to_apic('/api/mo/uni.json', json_content)

# Define output filename prefix
time_prefix = time.strftime("%Y%m%d-%H%M%S")

# Main Entrance for copy action
if __name__ == '__main__':

    if action['copy_json']:

        contract_json = get_json_file_from_apic()
        del contract_json['fvTenant']['attributes']['dn']
        with open('/usr/local/ACI/log/' + time_prefix + '_original_tenant.txt', 'w') as outfile:
            json.dump(contract_json, outfile)

    if action['paste_json']:

        # change tenant name before pushing to another APIC
        if from_tenant != to_tenant:
            contract_json['fvTenant']['attributes']['name'] = to_tenant
            with open('/usr/local/ACI/log/' + time_prefix + '_cloned_tenant.txt', 'w') as outfile:
                json.dump(contract_json, outfile)

        res = str(push_json_to_apic(contract_json))

    if res != '<Response [200]>':
        print 'Task failed'
    else:
        print 'Task is successfully completed.'

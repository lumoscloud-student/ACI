'''
Created by Wei Zixi (ziwei@cisco.com).

################################################################################
#         ____       _      _         _____                      _             #
#        |  _ \  ___| | ___| |_ ___  |_   _|__ _ __   __ _ _ __ | |_           #
#        | | | |/ _ \ |/ _ \ __/ _ \   | |/ _ \ '_ \ / _` | '_ \| __|          #
#        | |_| |  __/ |  __/ ||  __/   | |  __/ | | | (_| | | | | |_           #
#        |____/ \___|_|\___|\__\___|   |_|\___|_| |_|\__,_|_| |_|\__|          #
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

# Disable https certificate warning
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# Import credentials from credentials.py
from credentials import *
URL = apic['URL']
LOGIN = apic['LOGIN']
PASSWORD = apic['PASSWORD']

def delete_tenant():
    
    # Print ACI Tenant name for user input
    session = Session(URL, LOGIN, PASSWORD)
    resp = session.login()
    if not resp.ok:
        print '&& Could not login to APIC'
        sys.exit()

    tenant_list_input = Tenant.get(session)
    
    tenant_list = list()

    for tenant in tenant_list_input:
        tenant = tenant.get_json()['fvTenant']['attributes']['name']
        tenant_list.insert(0, tenant)


    tenant_list = list(enumerate(tenant_list))
    print 'ID\tTenant Name'
    for entry in tenant_list:
        print str(entry[0])+'\t'+str(entry[1])

    # Ask user input for tenant to delete
    print '\n'
    tenant_to_delete = raw_input('Pleae input Tenant ID you want to delete: ')
    tenant_to_delete = tenant_list[int(tenant_to_delete)][1]
    print '\n' + 'The ACI Tenant you want to delete is: '+ tenant_to_delete + '\n'
    ask_for_confirmation = raw_input('Please input "YES" or "Y" if you want to delete the tenant: ')
    if ask_for_confirmation == 'YES' or ask_for_confirmation == 'Y':
        print '\n' + 'Deleting tenant ' + tenant_to_delete
        url = '/api/node/mo/uni.json'
        json_content = '{"polUni":{"attributes":{"dn":"uni","status":"modified"},"children":[{"fvTenant":{"attributes":{"dn":"uni/tn-'+ tenant_to_delete +'","status":"deleted"},"children":[]}}]}}'
        json_content = ast.literal_eval(json_content)
        resp = session.push_to_apic(url, json_content)
        if resp.ok:
            print '\n' + 'Tenant ' + tenant_to_delete + 'has been deleted from ACI fabric.'
        else:
            print '\n' + 'Exectuion error, task aborted'
            sys.exit()
    else:
        print '\n' + 'Input error, task aborted.'
        sys.exit()

delete_tenant()
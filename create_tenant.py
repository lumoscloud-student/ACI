#!/usr/bin/python

'''
Modified by Wei Zixi (ziwei@cisco.com) from original ACItoolkit.

################################################################################
#         ____                _         _____                      _           #
#        / ___|_ __ ___  __ _| |_ ___  |_   _|__ _ __   __ _ _ __ | |_         #
#       | |   | '__/ _ \/ _` | __/ _ \   | |/ _ \ '_ \ / _` | '_ \| __|        #
#       | |___| | |  __/ (_| | ||  __/   | |  __/ | | | (_| | | | | |_         #
#        \____|_|  \___|\__,_|\__\___|   |_|\___|_| |_|\__,_|_| |_|\__|        #
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
#                                                                              #
#    The script create a tenant with the name given by user from first command #
#    argument. In case there is no argument given, tenant will be named as     #
#    "Cusomter-A"self.                                                         #
#    Within the tenant, the following component will be provisioned:           #
#    1 * Context, <Tenant>-L3                                                  #
#    3 * Bridge Domain, <Tenant>-BD1/BD2/BD3                                   #
#    1 * Subnet for each BD, 192.168.1.1/24, 192.168.2.1/24, 192.168.3.1/24    #
#    3 * EPG, WEB APP DB, being mapped to BD1/2/3                              #
#    2 * Contract, DB4APP, APP4WEB, each Contract has two filters,             #
#        SSH filter permit SSH access and ICMP filter permits ICMP traffic     #
#    All EPGs will be assigned to existing VMM domian if it's there.           #
#                                                                              #
################################################################################       
'''

import ast
import sys
import json
import time
from acitoolkit.acisession import *
from acitoolkit.acitoolkit import *
from credentials import *

# Import credentials from credentials.py
URL = apic['URL']
LOGIN = apic['LOGIN']
PASSWORD = apic['PASSWORD']

# Disable https certificate warning
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# Take tenant name from input, if there is no user input then make it as "Customer-A"
try:
    tenant_name = str(sys.argv[1])
except IndexError:
    print '>>> No tenant name being inputted, Tenant "Cusomter-A" will be created. <<<' + '\n' + '\n' + 'You can use "python create_tenant.py [Tenant Name]" syntax to create tenant with desired name.' + '\n'
    ask_for_confirmation = raw_input('Please input "YES" or "Y" if you want to create tenant "Customer-A": ')
    if ask_for_confirmation == 'YES' or ask_for_confirmation == 'Y':
        tenant_name = 'Customer-A'
    else:
        print '\n' + 'Input error, task aborted.'

# Define Tenant variables    
context_name = tenant_name + '-L3'
bd1_name = tenant_name + '-BD1'
bd2_name = tenant_name + '-BD2'
bd3_name = tenant_name + '-BD3'
app_pro_name = '3-Tier-App'

# Create the Tenant
tenant = Tenant(tenant_name)

# Create the Application Profile
app = AppProfile(app_pro_name, tenant)

# Create the EPG
epg1 = EPG('EPG-WEB', app)
epg2 = EPG('EPG-APP', app)
epg3 = EPG('EPG-DB', app)

# Create a Context and BridgeDomain
context = Context(context_name, tenant)
bd1 = BridgeDomain(bd1_name, tenant)
bd2 = BridgeDomain(bd2_name, tenant)
bd3 = BridgeDomain(bd3_name, tenant)
bd1.add_context(context)
bd2.add_context(context)
bd3.add_context(context)

# Create SVI and assign to Bridge Domain

subnetbd1 = Subnet('subnetbd1', bd1)
subnetbd2 = Subnet('subnetbd2', bd2)
subnetbd3 = Subnet('subnetbd3', bd3)
subnetbd1.set_addr('192.168.1.1/24')
subnetbd2.set_addr('192.168.2.1/24')
subnetbd3.set_addr('192.168.3.1/24')
bd1.add_subnet(subnetbd1)
bd2.add_subnet(subnetbd2)
bd3.add_subnet(subnetbd3)

# Place the EPG in the BD
epg1.add_bd(bd1)
epg2.add_bd(bd2)
epg3.add_bd(bd3)

# Attach EPG to VMM Domain
# To be define

# Add Contract to Tenant
contract_db4app = Contract('db4app', tenant)
entry1 = FilterEntry('icmp',
                applyToFrag='no',
                arpOpc='unspecified',
                dFromPort='unspecified',
                dToPort='unspecified',
                etherT='ip',
                prot='icmp',
                sFromPort='unspecified',
                sToPort='unspecified',
                tcpRules='unspecified',
                parent=contract_db4app)
entry2 = FilterEntry('ssh',
                applyToFrag='no',
                arpOpc='unspecified',
                dFromPort='22',
                dToPort='22',
                etherT='ip',
                prot='tcp',
                sFromPort='1',
                sToPort='65535',
                tcpRules='unspecified',
                parent=contract_db4app)

epg3.provide(contract_db4app)
epg2.consume(contract_db4app)

contract_app4web = Contract('app4web', tenant)
entry1 = FilterEntry('icmp',
                applyToFrag='no',
                arpOpc='unspecified',
                dFromPort='unspecified',
                dToPort='unspecified',
                etherT='ip',
                prot='icmp',
                sFromPort='unspecified',
                sToPort='unspecified',
                tcpRules='unspecified',
                parent=contract_app4web)
entry2 = FilterEntry('ssh',
                applyToFrag='no',
                arpOpc='unspecified',
                dFromPort='22',
                dToPort='22',
                etherT='ip',
                prot='tcp',
                sFromPort='1',
                sToPort='65535',
                tcpRules='unspecified',
                parent=contract_app4web)

epg2.provide(contract_app4web)
epg1.consume(contract_app4web)

# Login to APIC and create the tenant

session = Session(URL, LOGIN, PASSWORD)
session.login()
resp = tenant.push_to_apic(session)
if resp.ok:
   print 'Tenant has been successfully created.\n'

# Craft EPG MO url and JSON to associate EPG with VMM domain
# VMM domain name is being hardcoded here, alter the variable in accordance with your environment
vmm_domain = 'VMM-Philip'

epglist = EPG.get(session, parent=app, tenant=tenant)
for epg in epglist:
    epg = epg.get_json()['fvAEPg']['attributes']['name']
    epg_mo_url = '/api/node/mo/uni/tn-' + tenant_name + '/ap-' + app_pro_name + '/epg-' + epg + '.json'
    json_content = '{"fvRsDomAtt":{"attributes":{"tDn":"uni/vmmp-VMware/dom-' + vmm_domain +'","status":"created"},"children":[]}}'
    json_content = ast.literal_eval(json_content)
    resp = session.push_to_apic(epg_mo_url, json_content)
    if resp.ok:
        print 'EPG ' + epg + ' and VMM has been successfully associated.\n'

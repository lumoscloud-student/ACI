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
from acitoolkit.acisession import *
from acitoolkit.acitoolkit import *

# Decrypted and use credentials defined below
from credentials import *

# Disable https certificate warning
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def get_json_file_from_apic():

    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    vmm_domains = VmmDomain.get(session)
    print vmm_domains
    for domain in vmm_domains:
        print domain.get_parent()

get_json_file_from_apic()

#def get_egg_file_from_apic():
#
#    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
#    resp = session.login()
#    if not resp.ok:
#        print '%% Could not login to APIC'
#        sys.exit()
#
#    class_query_url = '/api/node/class/DomP.json'
#    result = session.get(class_query_url)
#    data = result.json()['imdata']
#    with open('./temp.txt', 'w') as outfile:
#            json.dump(data, outfile)
#
#get_egg_file_from_apic()

def get_egg_detail_from_apic():

    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    class_query_url = '/api/mo/uni/tn-HKJC-OA/ap-OA-App/epg-EPG-OA-App.json?rsp-subtree=full&rsp-prop-include=config-only'
    result = session.get(class_query_url)
    data = result.json()['imdata'][0]
    with open('./temp1.txt', 'w') as outfile:
            json.dump(data, outfile)

get_egg_detail_from_apic()

def get_epgdomain_from_apic():

    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    domains = EPGDomain.get(session)
    for domain in domains:
        print domain.get_json

get_epgdomain_from_apic()

def assign_vmm():
    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    tenant = Tenant('ziwei')
    app = AppProfile('app', tenant)
    epg = EPG('web', app)
    vmm = VmmDomain('VMM-Philip', None)
    epg.attach(vmm)

assign_vmm()
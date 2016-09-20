#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#        _____ _                  _____           _                            #
#       / ____(_)                / ____|         | |                           #
#      | |     _ ___  ___ ___   | (___  _   _ ___| |_ ___ _ __ ___  ___        #
#      | |    | / __|/ __/ _ \   \___ \| | | / __| __/ _ \ '_ ` _ \/ __|       #
#      | |____| \__ \ (_| (_) |  ____) | |_| \__ \ ||  __/ | | | | \__ \       #
#       \_____|_|___/\___\___/  |_____/ \__, |___/\__\___|_| |_| |_|___/       #
#                                        __/ |                                 #
#                                       |___/                                  #
#           _  __                       _____       _  _____ ______            #
#          | |/ /                      / ____|     | |/ ____|  ____|           #
#          | ' / ___  _ __ ___  __ _  | (___   ___ | | (___ | |__              #
#          |  < / _ \| '__/ _ \/ _` |  \___ \ / _ \| |\___ \|  __|             #
#          | . \ (_) | | |  __/ (_| |  ____) | (_) | |____) | |____            #
#          |_|\_\___/|_|  \___|\__,_| |_____/ \___/|_|_____/|______|           #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2016 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
# Licensed under the Apache License, Version 2.0 (the "License"); you may      #
# not use this file except in compliance with the License. You may obtain      #
# a copy of the License at                                                     #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################


'''
Created on 2016. 7. 27.

@author: "comfact"
'''

from ciscowebkit.common import *
from ciscowebkit.models import *
 
class Setting(Feature):
    
    def __init__(self):
        Feature.__init__(self, icon='fa-wrench')
        
        form = Form('Connect')
        form.addText('domain', 'Domain', 'input unique domain name')
        form.addText('ips', 'APIC Address', 'x.x.x.x/y.y.y.y/z.z.z.z')
        form.addText('user', 'User', 'input admin name')
        form.addPassword('pwd', 'Password', 'input admin password')
        self.form_panel = Panel('Add Connection', form, icon='fa-asterisk')
        
        for dom in ACI_Domain.objects.all():
            ACI.addDomain( dom.name, dom.controllers, dom.user, dom.password)
            
        self.info = None;
        
    def get(self, request, *cmd):
        
        apic_table = Table('Domain', 'Address', 'User', 'Password', 'Connected')
        for domain in ACI._order: apic_table.add(domain, str(ACI[domain].ips), ACI[domain].user, '*******', ACI[domain].connected, did=domain)
        
        if self.info:
            lo = Layout(Row(Col(self.info)))
            self.info = None
        else: lo = Layout()
        
        lo(
            Row(self.form_panel),
            Row(Panel('Connection List', apic_table, icon='fa-table'))
        )
        
        return lo
    
    def post(self, request, data, *cmd):
        apic = ACI.addDomain(data.domain, data.ips, data.user, data.pwd)
        
        if apic: 
            r = ACI_Domain.objects.create(name=data.domain, controllers=data.ips,user=data.user,password=data.pwd)
            self.info = InfoBlock(LC('Connection succeeded'),
                                  LC('The APIC %(domain)s is connected %(connected)s.', domain=apic.domain, connected=apic.connected)) 
        else: 
            self.info = InfoBlock(LC('Connection Failed'),
                                  LC('The APIC connection failed. Check the connection information.')) 
        return self.get(request, *cmd)
    
    def delete(self, request, data, *cmd):
        
        ACI.delDomain(data)
        
        try:
            pk = ACI_Domain.objects.get(name=data)
            pk.delete()
        except ACI_Domain.DoesNotExist:
            pass
        
        self.info = InfoBlock(LC('Connection Deleted'),
                              LC('The connection %(data)s has been removed.', data=data))
        
        return self.get(request, *cmd)

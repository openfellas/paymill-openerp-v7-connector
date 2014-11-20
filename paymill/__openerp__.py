# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Netbox (http://www.netbox.rs) All Rights Reserved.
#                    
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    'name': 'Paymill Connector',
    'version': '1.0',
    'depends': ['base','sale','account','account_voucher','web','web_m2x_options'],
    'author': 'openfellas',
    'category': 'Payment',
    'description': '''
This is the release of the Paymill connector linking OpenERP and
Paymill. This module allows you to use
payments, refunds, preauthorizations and also you can use Paymill plug-ins such as connect and refresh token.
    ''',
    'data': [
        'security/paymill_security.xml',
        'security/ir.model.access.csv',
        'paymill_data.xml',
        'paymill_view.xml',
        'base/res_partner_view.xml',
        'account_voucher/account_voucher_view.xml',
        'account/account_invoice_view.xml',
        'sale/wizard/preauth_wizard_view.xml',
        'sale/sale_order_view.xml',
        'translation_fix.sql'
    ],
    'js': ['static/src/js/paymill.js',
           'static/src/js/paymill_bridge.js'
    ],
    'css': ['static/src/css/paymill.css'],
}
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

from openerp.osv import fields, orm, osv
import base64
import os
import random
from openerp import tools
from openerp.tools.translate import _
from openerp.addons.paymill.paymill_config import execute_transaction, PAYMILL_PREAUTH_TRANSACTION

class paymill_preauth_wizard(orm.TransientModel):
    _name = 'paymill.preauth.wizard'

    def _get_image_fn(self, cr, uid, ids, name, args, context=None):
        image = self._get_image(cr, uid, context)
        return dict.fromkeys(ids, image)

    def _get_image(self, cr, uid, context=None):
        path = os.path.join('base','res','config_pixmaps','%d.png' % random.randrange(1,4))
        image_file = file_data = tools.file_open(path,'rb')
        try:
            file_data = image_file.read()
            return base64.encodestring(file_data)
        finally:
            if image_file != None:
                image_file.close()

    _columns = {
        'name': fields.char('Name'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'paymill_payment_information_id': fields.many2one('paymill.payment.information', 'Card', required=True),
        'amount': fields.float('Amount'),
        'config_logo': fields.function(_get_image_fn, string='Image', type='binary'),
    }

    _defaults ={
        'config_logo': _get_image,
    }

    def ochange_paymill_payment_information_id(self, cr, uid, ids, paymill_payment_information_id, context=None):
        res = {}
        if paymill_payment_information_id:
            paymill_config = self.pool.get('paymill.connect.configuration')
            config_ids = paymill_config.search(cr, uid, [])

            if config_ids:
                card = self.pool.get('paymill.payment.information').browse(cr, uid, paymill_payment_information_id).card_type
                allowed_cards = []
                for card_holder in paymill_config.browse(cr, uid, config_ids[0]).paymill_card_holder_ids:
                    allowed_cards.append(card_holder.card_id.name)

                    if card not in allowed_cards:
                        warning = {
                            'title': _('Warning!'),
                            'message': _('Preauthorization through Paymill is not possible! \n Payment card %s is not allowed.' % card)
                        }

                        res.update({
                            'value': {
                                'paymill_payment_information_id': False
                            },
                            'warning': warning
                        })
                        
                        return res

        return res

    def _get_openerp_transaction_dict(self, cr, uid, paymill_transaction, context):
        preauth_vals = {}
        preauth_vals.update(paymill_transaction.preauthorization)
        preauth_vals.update({
            'payment_id': context.get('preauth_payment_id',False),
            'preauthorization': paymill_transaction.preauthorization['id']
        })

        return {
            'transaction': paymill_transaction.id,
            'amount': paymill_transaction.amount,
            'origin_amount': paymill_transaction.origin_amount,
            'status': paymill_transaction.status,
            'description': paymill_transaction.description,
            'livemode': True if paymill_transaction.livemode else False,
            'is_fraud': True if paymill_transaction.is_fraud else False,
            'currency': paymill_transaction.currency,
            'created_at': paymill_transaction.created_at,
            'updated_at': paymill_transaction.updated_at,
            'response_code': paymill_transaction.response_code,
            'short_id': paymill_transaction.short_id,
            'app_id': paymill_transaction.app_id,
            'paymill_preauth_id': self.pool.get('paymill.preauthorization').create(cr, uid, preauth_vals, context)
        }

    def _prepare_data_for_transaction(self, cr, uid, ids, context):
        wizard_obj = self.browse(cr, uid, ids)[0]
        active_sale_order = self.pool.get('sale.order').browse(cr, uid, context.get('active_id',False))
        preauth_data = {}

        payment = wizard_obj.paymill_payment_information_id

        if payment:
            context.update({
                'preauth_payment_id': payment.id,
                'preauth_partner_id': wizard_obj.partner_id.id
            })
            preauth_data.update({
                'payment': payment.payment,
                'amount': int(wizard_obj.amount*100),
                'currency': active_sale_order.pricelist_id.currency_id.name,
                'description': '%s, %s' % (active_sale_order.partner_id.name, active_sale_order.name)
            })
            
        return preauth_data

    def _handle_transaction_result(self, cr, uid, ids, paymill_transaction, context):
        openerp_transaction_dict = self._get_openerp_transaction_dict(cr, uid, paymill_transaction, context)

        # Update payment and res partner
        payment_id = context.get('preauth_payment_id',False)
        openerp_transaction_dict.update({
            'partner_id': context.get('preauth_partner_id',False) 
        })
        self.pool.get('paymill.payment.information').write(cr, uid, payment_id, {'paymill_transaction_ids': [[0,0,openerp_transaction_dict]]})

        # Update sale order
        transaction_id = self.pool.get('paymill.transaction').search(cr, uid, [('transaction','=',openerp_transaction_dict.get('transaction',''))])[0]
        self.pool.get('sale.order').write(cr, uid, context.get('active_id', False), {'is_paymill_preauth': True, 'is_paymill_preauth_active': True, 'paymill_preauthorization_id': transaction_id})

    def check_order_allowed_currency(self, cr, uid, ids, context):
        paymill_config = self.pool.get('paymill.connect.configuration')
        config_ids = paymill_config.search(cr, uid, [])

        if config_ids:
            order_currency_id = self.pool.get('sale.order').browse(cr, uid, context['active_id']).pricelist_id.currency_id.id
            paymill_currency_ids = []
            for holder in paymill_config.browse(cr, uid, config_ids[0]).paymill_currency_holder_ids:
                paymill_currency_ids.append(holder.currency_id.id)

            if order_currency_id not in paymill_currency_ids:
                raise osv.except_osv(_('Error'),_('Prauthorization through Paymill is now possible! Order currency is not allowed'))

    def action_run_paymill_preauth(self, cr, uid, ids, context):
        if not context or 'active_id' not in context.keys():
            return
        # Check for sale order currency
        self.check_order_allowed_currency(cr, uid, ids, context)

        # 1. Prepare data for transaction  
        transaction_data = self._prepare_data_for_transaction(cr, uid, ids, context)

        # 2. Execute preauthorization
        paymill_transaction = execute_transaction(self, cr, uid, ids, transaction_data, PAYMILL_PREAUTH_TRANSACTION)

        # 3. Handle preauthorization transaction result            
        self._handle_transaction_result(cr, uid, ids, paymill_transaction, context)

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

import logging

from openerp.osv import fields, orm
from ..paymill_config import execute_transaction, get_paymill_account_journal, PAYMILL_CHECK_PREAUTH, PAYMILL_PREAUTH_VALID_STATUSES

_logger = logging.getLogger(__name__)

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'default_journal_id': fields.many2one('account.journal', 'Journal'),
        'default_payment_id': fields.many2one('paymill.payment.information', 'Paymill Payment'),
        'default_paymill_preauth': fields.char('Default Paymill Preauth'), # From SO
        'is_paymill_preauth': fields.boolean('Is Paymill Preauth'),
        'is_paymill_preauth_active': fields.boolean('Paymill Preauthorization Active'),
        'paymill_enable': fields.boolean('Paymill Enable')
    }

    _defaults = {
        'is_paymill_preauth': False,
        'is_paymill_preauth_active': False,
        'paymill_enable': False
    }

    def invoice_validate(self, cr, uid, ids, context=None):
        paymill_config = self.pool.get('paymill.connect.configuration')
        config_ids = paymill_config.search(cr, uid, [])

        if config_ids:
            invoice_currency_id = self.browse(cr, uid, ids[0]).currency_id.id
            paymill_currency_ids = []
            for holder in paymill_config.browse(cr, uid, config_ids[0]).paymill_currency_holder_ids:
                paymill_currency_ids.append(holder.currency_id.id)

            if invoice_currency_id in paymill_currency_ids:
                self.write(cr, uid, ids, {'paymill_enable': True})

        return super(account_invoice, self).invoice_validate(cr, uid, ids, context)

    def create(self, cr, uid, vals, context):
        if 'origin' in vals.keys() and vals['origin']:
            sale_order_dao = self.pool.get('sale.order')

            sale_id = sale_order_dao.search(cr, uid, [('name','=',vals['origin'])])
            sale_record = sale_order_dao.browse(cr, uid, sale_id[0]) if len(sale_id) == 1 else False

            if sale_record and sale_record.is_paymill_preauth:
                preauthorization = sale_record.paymill_preauthorization_id.paymill_preauth_id.preauthorization

                vals['default_paymill_preauth'] = preauthorization

                paymill_preauth_ids = self.pool.get('paymill.preauthorization').search(cr, uid, [('preauthorization','=',preauthorization)])

                vals['default_payment_id'] = self.pool.get('paymill.preauthorization').browse(cr, uid, paymill_preauth_ids[0]).payment_id.id
                
                journal_id = get_paymill_account_journal(self, cr, uid)
                vals['default_journal_id'] =  journal_id if journal_id else False

                vals['is_paymill_preauth'] = True
                vals['is_paymill_preauth_active'] = True

        return super(account_invoice,self).create(cr, uid, vals, context)

    def _get_openerp_payment_dict(self, cr, uid, paymill_payment, context):
            return {
                'payment': paymill_payment.id,
                'type': paymill_payment.type,
                'client': paymill_payment.client, 
                'card_type': paymill_payment.card_type,
                'country': paymill_payment.country,
                'expire_month': paymill_payment.expire_month,
                'expire_year': paymill_payment.expire_year,
                'last4': paymill_payment.last4,
                'created_at': paymill_payment.created_at,
                'updated_at': paymill_payment.updated_at,
                'app_id': paymill_payment.app_id,
            }

    def _prepare_data_for_transaction(self, cr, uid, ids, context):
        return {
            'preauthorization_id': self.browse(cr, uid, ids[0]).default_paymill_preauth
        }

    def _handle_transaction_result(self, cr, uid, ids, transaction, result, context):
        if transaction.status not in PAYMILL_PREAUTH_VALID_STATUSES:            
            result['context']['default_paymill_payment_information_id'] = False
            result['context']['default_journal_id'] = False
            result['context']['default_is_paymill_preauth_active'] = False

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).invoice_pay_customer(cr, uid, ids, context)

        # -- Check for preauthorisation and their valid status
        if self.browse(cr, uid, ids[0]).is_paymill_preauth_active:
            # 1. Prepare data for checking
            transaction_data = self._prepare_data_for_transaction(cr, uid, ids, context)

            # 2. Execute transaction checking
            transaction = execute_transaction(self, cr, uid, ids, transaction_data, PAYMILL_CHECK_PREAUTH)

            # 3. Handle check results
            self._handle_transaction_result(cr, uid, ids, transaction, result, context)

        return result

class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'paymill_transaction_id': fields.many2one('paymill.transaction', 'Paymill Transaction')
    }
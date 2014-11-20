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
from openerp.tools.translate import _
from ..paymill_config import execute_transaction, get_paymill_account_journal, PAYMILL_PAYMENT_TRANSACTION, PAYMILL_REFUND_TRANSACTION, PAYMILL_CHECK_PREAUTH, PAYMILL_PREAUTH_VALID_STATUSES

class account_voucher(orm.Model):
    _inherit = 'account.voucher'
            
    _columns = {
        'is_paymill': fields.boolean('Is Paymill'),
        'paymill_transaction_id': fields.many2one('paymill.transaction', 'Paymill Transaction'),
        'paymill_payment_information_id': fields.many2one('paymill.payment.information', 'Card'),
        'paymill_preauth': fields.char('Paymill Preauthorization'),
        'is_paymill_preauth': fields.boolean('Is Paymill Preauth'),
        'is_paymill_preauth_active': fields.boolean('Is Paymill Preauthorization Active'),
        'is_refund_and_paymill_journal': fields.boolean('Is Refund and Paymill Journal'),
    }

    _defaults = {
        'is_paymill_preauth': False,
        'is_refund_and_paymill_journal': False
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
                            'message': _('Register Payment through Paymill is not possible! \n Payment card %s is not allowed.' % card)
                        }

                        res.update({
                            'value': {
                                'paymill_payment_information_id': False
                            },
                            'warning': warning
                        })
                        
                        return res

        return res

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        res = super(account_voucher,self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)

        if not res:
            res = {}

        if journal_id:
            paymill_journal_id = get_paymill_account_journal(self, cr, uid)
            
            if journal_id == paymill_journal_id and 'active_model' not in context.keys():
                cash_journal_id = self.pool.get('account.journal').search(cr, uid, [('code','=','BNK1')])[0]

                res['value'].update({
                    'is_paymill': False,
                    'is_refund_and_paymill_journal': False,
                    'journal_id': cash_journal_id
                })
                warning = {
                    'title': _('Warning!'),
                    'message': _('Register Payment through Paymill is not implemented.')
                }

                return {'value': res['value'], 'warning': warning}
        
            elif journal_id == paymill_journal_id and self.pool.get(context['active_model']).browse(cr, uid, context['active_id']).paymill_enable:
                res['value'].update({
                    'is_paymill': True,
                })

                if context.get('invoice_type','') in ['out_refund','in_refund']:
                    res['value'].update({
                        'is_refund_and_paymill_journal': True
                    })

                elif context.get('invoice_type','') == 'out_invoice':
                    res['value'].update({
                        'is_refund_and_paymill_journal': False
                    })
            elif journal_id == paymill_journal_id and not self.pool.get(context['active_model']).browse(cr, uid, context['active_id']).paymill_enable:
                cash_journal_id = self.pool.get('account.journal').search(cr, uid, [('code','=','BNK1')])[0]

                res['value'].update({
                    'is_paymill': False,
                    'is_refund_and_paymill_journal': False,
                    'journal_id': cash_journal_id
                })
                warning = {
                    'title': _('Warning!'),
                    'message': _('Register Payment through Paymill is not possible! \n Currency of invoice is not allowed.')
                }

                return {'value': res['value'], 'warning': warning}

            else:
                res['value'].update({
                    'is_paymill': False,
                    'is_refund_and_paymill_journal': False
                })

        return res

    def ochange_paymill_transaction_id(self, cr, uid, ids, paymill_transaction_id, context=None):
        res = {}
#         if paymill_transaction_id:
#             res = {
#                 'value': {
#                     'amount': -float(self.pool.get('paymill.transaction').browse(cr, uid, paymill_transaction_id).amount)
#                 }
#             }

        return res

    def do_nothing(self, cr, uid, ids, context):
        return {'type': 'ir.actions.act_window_close'}

    def _get_openerp_transaction_dict(self, cr, uid, paymill_transaction, context):
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
        }

    def _get_openerp_refund_dict(self, cr, uid, paymill_transaction, context):
        return {
            'refund' : paymill_transaction.id,
            'amount' : paymill_transaction.amount,
            'status' : paymill_transaction.status,
            'description' : paymill_transaction.description,
            'livemode': paymill_transaction.livemode,
            'created_at': paymill_transaction.created_at,
            'updated_at': paymill_transaction.updated_at,
            'response_code': paymill_transaction.response_code,
            'app_id': paymill_transaction.app_id
        }

    def _prepare_data_for_transaction(self, cr, uid, ids, context):
        transaction_data = {}

        active_voucher = context.get('active_voucher', False)
        active_invoice = context.get('active_invoice', False)

        # -- Data for Refund
        if context.get('is_refund',False):
            transaction_data.update({
                'transaction_id': active_voucher.paymill_transaction_id.transaction,
                'amount': int(abs(active_voucher.amount)*100),
                'description': '%s, %s' % (active_voucher.partner_id.name, active_invoice.number)
            })

            return transaction_data

        # -- Data for Pay
        else:
            preauth_active = active_voucher.is_paymill_preauth_active
            
            transaction_data.update({
                'amount': int(active_voucher.amount*100),
                'currency': active_voucher.currency_id.name,
                'description': '%s, %s' % (active_voucher.partner_id.name, active_invoice.number),
                'preauth_active': preauth_active
            })
            
            if preauth_active:
                transaction_data.update({
                    'preauth': active_voucher.paymill_preauth
                })

            else:
                transaction_data.update({
                    'payment': active_voucher.paymill_payment_information_id.payment
                })
            
            return transaction_data

    def _handle_transaction_result(self, cr, uid, ids, paymill_transaction, context):
        active_voucher = context.get('active_voucher', False)

        # -- Handle Refund transaction result
        if context.get('is_refund',False):
            openerp_refund_dict = {}
            openerp_refund_dict = self._get_openerp_refund_dict(cr, uid, paymill_transaction, context)

            # Update paymill transaction and partner
            openerp_refund_dict.update({'partner_id': active_voucher.partner_id.id})

            values = {
                'paymill_refund_ids': [[0,0,openerp_refund_dict]],
            }
            values.update(paymill_transaction.transaction)

            self.pool.get('paymill.transaction').write(cr, uid, active_voucher.paymill_transaction_id.id, values)

        # -- Handle Pay transaction result
        else:
            openerp_transaction_dict = {}
            openerp_transaction_dict = self._get_openerp_transaction_dict(cr, uid, paymill_transaction, context)

            # Update paymill payment and partner
            openerp_transaction_dict.update({'partner_id': active_voucher.partner_id.id})
            self.pool.get('paymill.payment.information').write(cr, uid, active_voucher.paymill_payment_information_id.id, {'paymill_transaction_ids': [[0,0,openerp_transaction_dict]]})

            # Update account voucher
            transaction_id = self.pool.get('paymill.transaction').search(cr, uid, [('transaction','=',openerp_transaction_dict.get('transaction',''))])[0]
            self.write(cr, uid, ids, {'paymill_transaction_id': transaction_id})

            # Update account move line
            invoice_number = self.pool.get('account.invoice').browse(cr, uid, context.get('active_id')).number
            journal_id = get_paymill_account_journal(self, cr, uid)
            move_id = self.pool.get('account.move.line').search(cr, uid, [('name','=',invoice_number),('paymill_transaction_id','=',False),('journal_id','=',journal_id)])

            self.pool.get('account.move.line').write(cr, uid, move_id, {'paymill_transaction_id': transaction_id})

    def button_proforma_voucher(self, cr, uid, ids, context=None):
        result = super(account_voucher,self).button_proforma_voucher(cr, uid, ids, context)

        voucher = self.browse(cr, uid, ids[0])
        
        active_invoice = self.pool.get('account.invoice').browse(cr, uid, context.get('active_id',False))
        paymill_journal_id = get_paymill_account_journal(self, cr, uid)

        if voucher.journal_id.id == paymill_journal_id:
            # -- Save current active voucher browse record in context for later use in methods _prepare_data_for_transaction(...) and _handle_transaction_result(...)
            if not context: context = {}
            context.update({
                'active_voucher': voucher,
                'active_invoice': active_invoice
            })

            # Scenario 1. Invoice Pay
            if 'invoice_type' in context.keys() and context['invoice_type'] in ['in_invoice','out_invoice']:
                # -- If uid does not belong paymill user/paymill admin group, he still can select Paymill Journal in Payment Method field, but he can not select payment(card). In order to prevent ugly error, we add this type of check.
                if not voucher.paymill_payment_information_id:
                    raise osv.except_osv(_('Error'),_('Payment method is not selected!'))
                 
                context.update({'is_refund': False})

                # 1. Prepare data for transaction
                transaction_data = self._prepare_data_for_transaction(cr, uid, ids, context)

                # 2. Execute transaction
                paymill_transaction = execute_transaction(self, cr, uid, ids, transaction_data, PAYMILL_PAYMENT_TRANSACTION, context)

                # 3. Handle transaction result
                self._handle_transaction_result(cr, uid, ids, paymill_transaction, context)

            # Scenario 2. Invoice Refund
            elif 'invoice_type' in context.keys() and context['invoice_type'] in ['in_refund','out_refund']:
                # -- If uid does not belong paymill user/paymill admin group, he still can select Paymill Journal in Payment Method field, but he can not select transaction. In order to prevent ugly error, we add this type of check.
                if not voucher.paymill_transaction_id:
                    raise osv.except_osv(_('Error'),_('Paymill Transaction is not selected!'))

                context.update({'is_refund': True})

                # 1. Prepare data for transaction
                transaction_data = self._prepare_data_for_transaction(cr, uid, ids, context)

                # 2. Execute transaction
                paymill_transaction = execute_transaction(self, cr, uid, ids, transaction_data, PAYMILL_REFUND_TRANSACTION, context)

                # 3. Handle transaction result
                self._handle_transaction_result(cr, uid, ids, paymill_transaction, context)

        return result
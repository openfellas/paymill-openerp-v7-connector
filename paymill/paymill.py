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

from openerp.osv import fields, orm, osv
from datetime import date
import datetime
import httplib2
import json
from urllib import urlencode
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp.addons.paymill.paymill_config import execute_transaction, update_paymill_keys, PAYMILL_NEW_CARD, PAYMILL_CONNECT_URL, PAYMILL_CONNECT_HTTP_METHOD, PAYMILL_REFRESH_TOKEN_GRANT_TYPE, PAYMILL_CONNECT_HTTP_HEADER_CONTENT_TYPE

_logger = logging.getLogger(__name__)

CONNECT_PERMISSIONS = [
'transactions_r',
'transactions_w',
'transactions_rw',
'refunds_r',
'refunds_w',
'refunds_rw',
'clients_r',
'clients_w',
'clients_rw',
'offers_r',
'offers_w',
'offers_rw',
'frauds_r',
'frauds_w',
'frauds_rw',
'subscriptions_r',
'subscriptions_w',
'subscriptions_rw',
'payments_r',
'payments_w',
'payments_rw',
'preauthorizations_r',
'preauthorizations_w',
'preauthorizations_rw',
'webhooks_r',
'webhooks_w',
'webhooks_rw'
]

MONTHS = [
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10'),
    ('11','11'),
    ('12','12')
]

# Regarding Ticket PAYMILL-22
def convert_number_currency_format(values):
    if 'amount' in values.keys():
        amount = float(values['amount'])
        converted_amount = amount / 100
        values['amount'] = '%0.2f' % converted_amount

    if 'origin_amount' in values.keys():
        origin_amount = float(values['origin_amount'])
        converted_origin_amount = origin_amount / 100
        values['origin_amount'] = '%0.2f' % converted_origin_amount

    if 'created_at' in values.keys() and 'updated_at' in values.keys():
        values['created_at'] = datetime.datetime.fromtimestamp(int(values['created_at'])).strftime('%Y-%m-%d %H:%M:%S')
        values['updated_at'] = datetime.datetime.fromtimestamp(int(values['updated_at'])).strftime('%Y-%m-%d %H:%M:%S')

class paymill_payment_information(orm.Model):
    _name = 'paymill.payment.information'

    _rec_name = 'payment'

    def _get_selection(self, cr, uid, context=None):
        res = [] 
        for x in range(0,4):
            res.append(((date.today() + relativedelta(years=x)).strftime('%Y'), (date.today() + relativedelta(years=x)).strftime('%Y')))

        return res

    _columns = {
        'name': fields.char('Name'),
        'payment': fields.char('Payment'),
        'type': fields.char('Type'),
        'client': fields.char('Client'),
        'card_type': fields.char('Card Type'),
        'country': fields.char('Country'),
        'expire_month': fields.char('Expire Month'),
        'expire_year': fields.char('Expire Year'),
        'last4': fields.char('Last4'),
        'created_at': fields.integer('Created At'),
        'updated_at': fields.integer('Updated At'),
        'app_id': fields.char('App'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'paymill_transaction_ids': fields.one2many('paymill.transaction', 'paymill_payment_information_id', 'Transactions'),
        'code': fields.char('Code'), # Direct payment
        'holder': fields.char('Holder'), # Direct payment
        'account': fields.char('Account'), # Direct payment
        'is_debit': fields.boolean('Is Debit'), # Direct payment
        'dummy': fields.char(''),
        'test_dummy': fields.dummy(string='Test Dummy', type="char"),
        'card_number_c1': fields.dummy(string='Card Number', type='char', size=4, required=True),
        'card_number_c2': fields.dummy(string='Card Number', type='char', size=4, required=True),
        'card_number_c3': fields.dummy(string='Card Number', type='char', size=4, required=True),
        'card_number_c4': fields.dummy(string='Card Number', type='char', size=4, required=True),
        'cvc_code': fields.dummy(string='CVC', type='char', required=True),
        'partner_name': fields.dummy(string='Partner Name', type='char'),
        'expiry_month': fields.dummy(string='Expiry Month', type='selection', selection=MONTHS, required=True),
        'expiry_year': fields.dummy(string='Expiry Year', type='selection', selection=_get_selection, required=True),
    }

    _defaults = {
        'is_debit': False
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = []
        for record in self.read(cr, uid, ids, ['last4','card_type', 'expire_month','expire_year'], context=context):
            res.append((record['id'], '%s, **************%s, %s/%s' % (record['card_type'],record['last4'],record['expire_month'],record['expire_year'])))

        return res

    def _get_openerp_payment_dict(self, cr, uid, paymill_transaction, context):
        return {
            'payment': paymill_transaction.id,
            'type': paymill_transaction.type,
            'client': paymill_transaction.client, 
            'card_type': paymill_transaction.card_type,
            'country': paymill_transaction.country,
            'expire_month': paymill_transaction.expire_month,
            'expire_year': paymill_transaction.expire_year,
            'last4': paymill_transaction.last4,
            'created_at': paymill_transaction.created_at,
            'updated_at': paymill_transaction.updated_at,
            'app_id': paymill_transaction.app_id,
        }
        
    def _prepare_data_for_transaction(self, cr, uid, args, context):
        transaction_data = {}

        transaction_data.update({
            'token': args['token']
        })

        return transaction_data
        
    def _handle_transaction_result(self, cr, uid, ids, paymill_transaction, context):
        openerp_payment_dict = self._get_openerp_payment_dict(cr, uid, paymill_transaction, context)
                    
        return openerp_payment_dict
    
    def get_paymill_payment_object(self, cr, uid, args, context):
        _logger.info('Processing payment...')

        if not context:
            context = {}

        # 1. Prepare data for transaction
        transaction_data = self._prepare_data_for_transaction(cr, uid, args, context)

        # 2. Execute transaction
        paymill_transaction = execute_transaction(self, cr, uid, False, transaction_data, PAYMILL_NEW_CARD)

        _logger.info('Processing payment finished!')

        # 3. Handle transaction result
        return self._handle_transaction_result(cr, uid, False, paymill_transaction, context)

class paymill_transaction(orm.Model):
    _name = 'paymill.transaction'

    _rec_name = 'transaction'

    _columns = {
        'name': fields.char('Name'),
        'transaction': fields.char('Transaction'),
        'amount': fields.char('Amount'),
        'origin_amount': fields.char('Original Amount'),
        'status': fields.char('Status'),
        'description': fields.char('Description'),
        'livemode': fields.boolean('Live Mode'),
        'is_fraud': fields.boolean('Is Fraud'),
        'currency': fields.char('Currency'),
        'created_at': fields.datetime('Created At'),
        'updated_at': fields.datetime('Updated At'),
        'response_code': fields.integer('Response Code'),
        'short_id': fields.char('Short ID'),
        'app_id': fields.char('App'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'paymill_payment_information_id': fields.many2one('paymill.payment.information', 'Payment Information'),
        'paymill_payment_last_four_related': fields.related('paymill_payment_information_id', 'last4', type='char', string='Last Four'),
        'paymill_payment_expiry_month_related': fields.related('paymill_payment_information_id', 'expire_month', type='char', string='Expire Month'),
        'paymill_payment_expiry_year_related': fields.related('paymill_payment_information_id', 'expire_year', type='char', string='Expire Year'),
        'paymill_refund_ids': fields.one2many('paymill.refund', 'paymill_transaction_id', 'Refunds'),
        'paymill_preauth_id': fields.many2one('paymill.preauthorization', 'Preauthorization')
    }

    def create(self, cr, uid, values, context=None):
        convert_number_currency_format(values)

        return super(paymill_transaction, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        convert_number_currency_format(values)

        return super(paymill_transaction, self).write(cr, uid, ids, values, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, '**************%s, %s , %s %s' % (record.paymill_payment_information_id.last4, record.created_at, record.amount, record.currency)))

        return res

class paymill_refund(orm.Model):
    _name = 'paymill.refund'

    _rec_name = 'refund'

    _columns = {
        'name': fields.char('Name'),
        'refund' : fields.char('Refund'),
        'amount' : fields.char('Amount'),
        'status' : fields.char('Status'),
        'description' : fields.char('Description'),
        'livemode': fields.boolean('Live Mode'),
        'created_at': fields.datetime('Created At'),
        'updated_at': fields.datetime('Updated At'),
        'response_code': fields.integer('Response Code'),
        'app_id': fields.char('App'),
        'paymill_transaction_id': fields.many2one('paymill.transaction', 'Transaction'),
        'partner_id': fields.many2one('res.partner', 'Partner')
    }

    def create(self, cr, uid, values, context=None):
        convert_number_currency_format(values)

        return super(paymill_refund, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        convert_number_currency_format(values)

        return super(paymill_refund, self).write(cr, uid, ids, values, context=context)

class paymill_preauthorization(orm.Model):
    _name = 'paymill.preauthorization'

    _rec_name = 'preauthorization'

    _columns = {
        'name': fields.char('Name'),
        'preauthorization': fields.char('Preauthorization'),
        'description': fields.char('Description'),
        'amount': fields.char('Amount'),
        'currency': fields.char('Currency'),
        'status': fields.char('Status'),
        'livemode': fields.boolean('Live Mode'),
        'created_at': fields.datetime('Created At'),
        'updated_at': fields.datetime('Updated At'),
        'app_id': fields.char('App'),
        'payment_id' : fields.many2one('paymill.payment.information', 'Payment')
    }

    def create(self, cr, uid, values, context=None):
        convert_number_currency_format(values)

        return super(paymill_preauthorization, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        convert_number_currency_format(values)

        return super(paymill_preauthorization, self).write(cr, uid, ids, values, context=context)

class paymill_connect_configuration(orm.Model):
    _name = 'paymill.connect.configuration'

    _columns = {
        # General
        'name': fields.char('Name'),
        'client_id': fields.char('App-ID', required=True),
        'client_secret': fields.char('Client secret', required=True),
        'journal_id': fields.many2one('account.journal', 'Account Journal'),
        'state': fields.selection((('active','Active'),('inactive','Inactive'),('error','Error')), 'Status'),
        'error': fields.char('Error'),
        'error_description': fields.text('Error Description'),
        'live_mode': fields.boolean('Live Mode'),
        'test_mode': fields.boolean('Test Mode'),
        'is_live': fields.boolean('Is Live'),
        'is_initialized': fields.boolean('Is Initialised'),
        'refresh_token': fields.char('Refresh Token'),
        'live_public_key': fields.char('Live Public Key'),
        'live_private_key': fields.char('Live Private Key'),
        'test_public_key': fields.char('Test Public Key'),
        'test_private_key': fields.char('Test Private Key'),
        # Transactions
        'transactions_r': fields.boolean('Read'),
        'transactions_w': fields.boolean('Write', readonly=True),
        'transactions_rw': fields.boolean('Read/Write', readonly=True),
        # Refunds
        'refunds_r': fields.boolean('Read'),
        'refunds_w': fields.boolean('Write', readonly=True),
        'refunds_rw': fields.boolean('Read/Write'),
        # Clients
        'clients_r': fields.boolean('Read'),
        'clients_w': fields.boolean('Write'),
        'clients_rw': fields.boolean('Read/Write'),
        # Offers
        'offers_r': fields.boolean('Read'),
        'offers_w': fields.boolean('Write'),
        'offers_rw': fields.boolean('Read/Write'),
        # Frauds
        'frauds_r': fields.boolean('Read'),
        'frauds_w': fields.boolean('Write'),
        'frauds_rw': fields.boolean('Read/Write'),
        # Subscriptions
        'subscriptions_r': fields.boolean('Read'),
        'subscriptions_w': fields.boolean('Write'),
        'subscriptions_rw': fields.boolean('Read/Write'),
        # Payments
        'payments_r': fields.boolean('Read'),
        'payments_w': fields.boolean('Write', readonly=True),
        'payments_rw': fields.boolean('Read/Write'),
        # Preauthorizations
        'preauthorizations_r': fields.boolean('Read'),
        'preauthorizations_w': fields.boolean('Write', readonly=True),
        'preauthorizations_rw': fields.boolean('Read/Write', readonly=True),
        # Webhooks
        'webhooks_r': fields.boolean('Read'),
        'webhooks_w': fields.boolean('Write'),
        'webhooks_rw': fields.boolean('Read/Write'),
        # For allowed currencies and cards
        'paymill_currency_holder_ids': fields.one2many('paymill.currency.holder', 'paymill_connect_configuration_id', 'Allowed Currencies'),
        'paymill_card_holder_ids': fields.one2many('paymill.card.holder', 'paymill_connect_configuration_id', 'Allowed Cards')
    }
    
    _defaults = {
        'is_initialized': False
    }

    def _check_unique_card(self, cr, uid, ids, context=None):
        cards_ids = []
        for card_holder in self.browse(cr, uid, ids[0]).paymill_card_holder_ids:
            cards_ids.append(card_holder.card_id.id)

        if len(cards_ids) != len(set(cards_ids)):
            return False

        return True

    _constraints = [(_check_unique_card, _('Error: UNIQUE CARD'), ['paymill_card_holder_ids'])]

    def create(self, cr, uid, vals, context=None):
        ids = self.search(cr, uid, [], context)
        if len(ids):
            raise osv.except_osv(_('Error!'),_('Configuration record has already been created!'))

        return super(paymill_connect_configuration, self).create(cr, uid, vals, context)

    def get_authenticate_config(self, cr, uid, args, context=None):
        _logger.info('-- Method Call get_authenticate_config started. Arguments %s ...' % str(args))

        config = self.pool.get('paymill.connect.configuration').browse(cr, uid, self.search(cr, uid, [], limit=1, order='id DESC', context=context))[0]

        allowed_permissions = []
        for field_name, value in self.read(cr, uid, config.id, CONNECT_PERMISSIONS).iteritems():
            if value and field_name != 'id':
                allowed_permissions.append(field_name)

        scope = ' '.join(allowed_permissions) if allowed_permissions else ''

        return {
            'client_secret': config.client_secret,
            'client_id': config.client_id,
            'scope': scope,
            'refresh_token': config.refresh_token
        }

        _logger.info('-- Method Call get_authenticate_config finshed successfully. Arguments %s ...' % str(args))
    
    def _return_card_currency_holder_ids(self, cr, uid, connect_config_id, cards, currencies):
        paymill_card_dao = self.pool.get('paymill.card')
        paymill_card_holder_dao = self.pool.get('paymill.card.holder')
        res_currency_dao = self.pool.get('res.currency')
        paymill_currency_holder_dao = self.pool.get('paymill.currency.holder')
        _logger.info('------ Config ID %s Cards %s Currencies %s' % (str(connect_config_id),str(cards),str(currencies)))
        cards_holder_ids = []
        for card in cards:
            _logger.info('------ Card name %s ...' % str(card))
            card_id = paymill_card_dao.search(cr, uid, [('name','=',card)])

            _logger.info('------ Card search results %s ...' % str(card_id))    

            if not len(card_id):
                card_id = paymill_card_dao.create(cr, uid, {'name': card})
                _logger.info('------ Card created! New ID -> %s ...' % str(card_id))
            else:
                card_id = card_id[0]

            card_holder_id = paymill_card_holder_dao.search(cr, uid, [('card_id','=',card_id)])
        
            _logger.info('------ Card holder search results %s ...' % str(card_holder_id))  
 
            if not(card_holder_id):
                card_holder_id = paymill_card_holder_dao.create(cr, uid, {'card_id': card_id, 'paymill_connect_configuration_id': connect_config_id})

                _logger.info('------ Card Holder created! New ID -> %s ...' % str(card_holder_id))

            cards_holder_ids.append(card_holder_id if type(card_holder_id) is long else card_holder_id[0])

        currency_holder_ids = []
        for curr in currencies:
            curr_id = res_currency_dao.search(cr, uid, [('name','=',curr)])
            if not len(curr_id):
                curr_id = res_currency_dao.create(cr, uid, {'name': curr})
            else:
                curr_id = curr_id[0]

            currency_holder_id = paymill_currency_holder_dao.search(cr, uid, [('currency_id','=',curr_id)])

            if not(currency_holder_id):
                currency_holder_id = paymill_currency_holder_dao.create(cr, uid, {'currency_id': curr_id, 'paymill_connect_configuration_id': connect_config_id})

            currency_holder_ids.append(currency_holder_id if type(currency_holder_id) is long else currency_holder_id[0])

        return cards_holder_ids, currency_holder_ids

    def update_paymill_connect_configuration(self, cr, uid, args, context=None):
        _logger.info('------ Method Call paymill_connect_configuration started. Arguments %s ...' % str(args))

        if not args:
            _logger.info('------ Method Call update_paymill_connect_configuration finished with failure. No arguments supplied. Arguments -> %s ...' % str(args))
            return False

        vals = {}

        ids = self.pool.get('paymill.connect.configuration').search(cr, uid, [], limit=1, order='id DESC', context=context)[0]
    
        _logger.info('------ CONFIG ID %s ...' % str(ids))    

        if 'error' in args.keys():
            vals.update({
                'state': 'error',
                'error': args.get('error',''),
                'error_description': args.get('error_description',''),
            })

        else:
            cards_holder_ids, curr_holder_ids = self._return_card_currency_holder_ids(cr, uid, ids, args.get('cards',[]), args.get('currencies',[]))

            _logger.info('------ CARD HOLDER IDS -> %s CURRENCY HOLDER IDS-> %s ' % (str(cards_holder_ids),str(curr_holder_ids)))
            
            live_mode = False
            if args.get('live_mode',False):
                live_mode = True
            if args.get('test_mode',False):
                live_mode = False
            
            vals.update({
                'state': 'active',
                'live_public_key': args['public_key'] if live_mode else '',
                'live_private_key': args['private_key'] if live_mode else '',
                'test_public_key': args['public_key'] if not live_mode else '',
                'test_private_key': args['private_key'] if not live_mode else '',
                'live_mode': args.get('live_mode',False),
                'test_mode': args.get('test_mode',False),
                'is_live': live_mode,
                'refresh_token': args.get('refresh_token',''),
                'paymill_currency_holder_ids': [[6,0,curr_holder_ids]],
                'paymill_card_holder_ids': [[6,0,cards_holder_ids]],
                'is_initialized': args.get('is_initialized',False)
            })

            # -- Update ir_config
            update_paymill_keys(self, cr, uid, args, context)

        self.write(cr, uid, ids, vals)

        _logger.info('------ Method Call update_paymill_connect_configuration is Finished successfully. Arguments %s Values %s' % (str(args), str(vals)))
        
        return True

    def refresh_token(self, cr, uid, context=None):
        h = httplib2.Http()
        config = self.get_authenticate_config(cr, uid, None)
        ids = self.search(cr, uid, [])

        data = dict(
            grant_type=PAYMILL_REFRESH_TOKEN_GRANT_TYPE,
            scope=config.get('scope',''),
            refresh_token=config.get('refresh_token',''), 
            client_id=config.get('client_id',''),
            client_secret=config.get('client_secret',''),
        )

        _logger.error(' - Paymill refresh token started with following data --> %s' %  str(data))

        resp, content = h.request(PAYMILL_CONNECT_URL, PAYMILL_CONNECT_HTTP_METHOD, urlencode(data), headers={'content-type': PAYMILL_CONNECT_HTTP_HEADER_CONTENT_TYPE})
        
        _logger.info(' - Paymill Refresh Token - Request Received. Details: "%s", Response:"%s"' % (content, resp))

        if isinstance(content, str):
            content = json.loads(content)

        if 'error' in content.keys():
            raise osv.except_osv(_('Error'), '%s. \n Details - %s' % (content['error'],content['error_description']))

        vals = {}
        # - Get data from content
        cards_holder_ids, curr_holder_ids = self._return_card_currency_holder_ids(cr, uid, ids, content.get('methods',[]), content.get('currencies',[]))
        
        access_keys = content['access_keys']
        
        live_mode = False
        if content['livemode']:
            live_mode = True
        else:
            live_mode = False
        vals.update({
            'live_public_key': access_keys['live']['public_key'] if 'live' in access_keys else '',
            'live_private_key': access_keys['live']['private_key'] if 'live' in access_keys else '',
            'test_public_key': access_keys['test']['public_key'] if 'test' in access_keys else '',
            'test_private_key': access_keys['test']['private_key'] if 'test' in access_keys else '',
            'live_mode': True if content['livemode'] else False,
            'test_mode': True if not content['livemode'] else False,
            'is_live': live_mode,
            'refresh_token': content['refresh_token'],
            'paymill_currency_holder_ids': [[6,0,curr_holder_ids]],
            'paymill_card_holder_ids': [[6,0,cards_holder_ids]]
                     
        })

        # - Update Paymill configuration
        self.write(cr, uid, ids, vals)
        
        # - Update ir_config
        update_paymill_keys(self, cr, uid, {'private_key': vals['live_private_key'] if vals['live_mode'] else vals['test_private_key'],
                                             'public_key': vals['live_public_key'] if vals['live_mode'] else vals['test_public_key']}, context)
class paymill_currency_holder(orm.Model):
    _name = 'paymill.currency.holder'

    _columns = {
        'name': fields.char('Name'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'paymill_connect_configuration_id': fields.many2one('paymill.connect.configuration', 'Paymill Configuration', required=True, ondelete='cascade')
    }

class paymill_card(orm.Model):
    _name = 'paymill.card'

    _columns = {
        'name': fields.char('Name'),
        'card_type': fields.char('Type'),
        'description': fields.text('Description')
    }

    def _check_unique_insesitive(self, cr, uid, ids, context=None):
        all_names = []
        for paymill_card in self.browse(cr, uid, self.search(cr, uid, [], context)):
            if paymill_card.id in ids:
                continue
            all_names.append(paymill_card.name.upper())

        for current_card in self.browse(cr, uid, ids, context):
            if current_card.name.upper() in all_names:
                return False

        return True

    _constraints = [(_check_unique_insesitive, _('Error: UNIQUE NAME'), ['name'])]

class paymill_card_holder(orm.Model):
    _name = 'paymill.card.holder'

    _columns = {
        'name': fields.char('Name'),
        'card_id': fields.many2one('paymill.card', 'Card'),
        'card_type': fields.related('card_id', 'card_type', type='char', string='Card Type'),
        'paymill_connect_configuration_id': fields.many2one('paymill.connect.configuration', 'Paymill Configuration', required=True, ondelete='cascade')
    }

class paymill_connect_configuration_wizard(orm.TransientModel):
    _name = 'paymill.connect.configuration.wizard'
    _inherit = 'res.config.settings'

    _columns = {
        # General
        'name': fields.char('Name'),
        'client_id': fields.char('App-ID', required=True),
        'client_secret': fields.char('Client secret', required=True),
        'journal_id': fields.many2one('account.journal', 'Account Journal'),
        'state': fields.selection((('active','Active'),('inactive','Inactive'),('error','Error')), 'Status'),
        'error': fields.char('Error'),
        'error_description': fields.text('Error Description'),
        'live_mode': fields.boolean('Live Mode'),
        'is_initialized': fields.boolean('Is Initialized'),
        'test_mode': fields.boolean('Test Mode'),
        'is_live': fields.boolean('Is Live'),
        'refresh_token': fields.char('Refresh Token'),
        'live_public_key': fields.char('Live Public Key'),
        'live_private_key': fields.char('Live Private Key'),
        'test_public_key': fields.char('Test Public Key'),
        'test_private_key': fields.char('Test Private Key'),
        # Transactions
        'transactions_r': fields.boolean('Read'),
        'transactions_w': fields.boolean('Write', readonly=True),
        'transactions_rw': fields.boolean('Read/Write', readonly=True),
        # Refunds
        'refunds_r': fields.boolean('Read'),
        'refunds_w': fields.boolean('Write', readonly=True),
        'refunds_rw': fields.boolean('Read/Write'),
        # Clients
        'clients_r': fields.boolean('Read'),
        'clients_w': fields.boolean('Write'),
        'clients_rw': fields.boolean('Read/Write'),
        # Offers
        'offers_r': fields.boolean('Read'),
        'offers_w': fields.boolean('Write'),
        'offers_rw': fields.boolean('Read/Write'),
        # Frauds
        'frauds_r': fields.boolean('Read'),
        'frauds_w': fields.boolean('Write'),
        'frauds_rw': fields.boolean('Read/Write'),
        # Subscriptions
        'subscriptions_r': fields.boolean('Read'),
        'subscriptions_w': fields.boolean('Write'),
        'subscriptions_rw': fields.boolean('Read/Write'),
        # Payments
        'payments_r': fields.boolean('Read'),
        'payments_w': fields.boolean('Write', readonly=True),
        'payments_rw': fields.boolean('Read/Write'),
        # Preauthorizations
        'preauthorizations_r': fields.boolean('Read'),
        'preauthorizations_w': fields.boolean('Write', readonly=True),
        'preauthorizations_rw': fields.boolean('Read/Write', readonly=True),
        # Webhooks
        'webhooks_r': fields.boolean('Read'),
        'webhooks_w': fields.boolean('Write'),
        'webhooks_rw': fields.boolean('Read/Write'),
    }

    _defaults = {
        'state': 'inactive',
        'transactions_w': True,
        'transactions_rw': True,
        'refunds_w': True,
        'payments_w': True,
        'preauthorizations_w': True,
        'preauthorizations_rw': True,
        'is_initialized': False
    }
    
    def write(self, cr, user, ids, vals, context=None):
        paymill_connect_dao = self.pool.get('paymill.connect.configuration')
        config_ids = paymill_connect_dao.search(cr, user, [], limit=1, order='id DESC', context=context)

        paymill_connect_dao.write(cr, user, config_ids, vals)
        
        # We don't update wizard object.
        return True

    def configure_currencies_and_cards(self, cr, uid, ids, context=None):
        paymill_connect_dao = self.pool.get('paymill.connect.configuration')
        config = paymill_connect_dao.browse(cr, uid, paymill_connect_dao.search(cr, uid, [], limit=1, order='id DESC', context=context))[0]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Configure Allowed Currencies',
            'res_model': 'paymill.connect.configuration',
            'res_id': config.id,
            'view_mode': 'form',
        }

    def get_default_all(self, cr, uid, fields, context=None):
        paymill_connect_dao = self.pool.get('paymill.connect.configuration')

        config_ids = paymill_connect_dao.search(cr, uid, [], limit=1, order='id DESC', context=context)
        if not config_ids:
            return {'name': ''}

        fields = ['name','client_id','client_secret','journal_id','state','error','error_description','live_mode','test_mode','refresh_token','live_public_key','live_private_key','test_public_key','test_private_key']
        fields.extend(CONNECT_PERMISSIONS)

        config = paymill_connect_dao.read(cr, uid, config_ids[0], fields, context=context)

        res = {}
        if config:
            for field_name, value in config.iteritems():
                res[field_name] = value
    
        return res

    def set_all(self, cr, uid, ids, context):
        paymill_connect_dao = self.pool.get('paymill.connect.configuration')

        config_ids = paymill_connect_dao.search(cr, uid, [], limit=1, order='id DESC', context=context)
        if config_ids:
            current_vals = paymill_connect_dao.copy_data(cr, uid, config_ids[0], context=context)
            
            # Remove old configuration.
            paymill_connect_dao.unlink(cr, uid, config_ids)

            # Create new one.
            paymill_connect_dao.create(cr, uid, current_vals)
            
        else:
            wizard_ids = self.search(cr, uid, [])

            current_vals = self.copy_data(cr, uid, wizard_ids[0], context=context)

            paymill_connect_dao.create(cr, uid, current_vals)

    def refresh_token(self, cr, uid, ids, context=None):
        self.pool.get('paymill.connect.configuration').refresh_token(cr, uid)

    def paymill_connect(self, cr, uid, ids, context):
        # Action will be performed with javascript.
        return False

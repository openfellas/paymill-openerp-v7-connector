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

import pymill
from openerp.tools.translate import _
from openerp.osv import osv

_logger = logging.getLogger(__name__)

################################## CONSTANTS ##################################

PAYMILL_PREAUTH_VALID_STATUSES = ['closed']

ALLOWED_RESPONSE_CODES = [10002,20000]

# -- Paymill Keys -> XML ids
PAYMILL_PRIVATE_KEY_XML_ID = 'paymill_private_key_XML_id'
PAYMILL_PUBLIC_KEY_XML_ID = 'paymill_public_key_XML_id'

# -- Paymill Connect Configuration
PAYMILL_CONNECT_URL = 'https://connect.paymill.com/token'
PAYMILL_CONNECT_GRANT_TYPE = 'authorization_code'
PAYMILL_CONNECT_HTTP_HEADER_CONTENT_TYPE = 'application/x-www-form-urlencoded'
PAYMILL_CONNECT_HTTP_METHOD = 'POST'

# -- Paymill Refresh Token Configuration
PAYMILL_REFRESH_TOKEN_GRANT_TYPE = 'refresh_token'

# -- Paymill Transaction Signals
PAYMILL_PAYMENT_TRANSACTION = 'payment_transaction'
PAYMILL_REFUND_TRANSACTION = 'refund_transaction'
PAYMILL_PREAUTH_TRANSACTION = 'preauth_transaction'
PAYMILL_CHECK_PREAUTH = 'preauth_checking'
PAYMILL_NEW_CARD = 'new_card'

# -- Translated Paymill response codes/errors
PAYMILL_RESPONSE_ERRORS = {
    'Payment not Found': _('Payment not Found!'),
    'General undefined response.': _('General undefined response.'),
    'Still waiting on something.': _('Still waiting on something.'),
    'General success response.': _('General success response.'),
    'General problem with data.': _('General problem with data.'),
    'Problem with creditcard data.': _('Problem with creditcard data.'),
    'Problem with cvv.': _('Problem with cvv.'),
    'Card expired or not yet valid.': _('Card expired or not yet valid.'),
    'Limit exceeded.': _('Limit exceeded.'),
    'Card invalid.': _('Card invalid.'),
    'expiry date not valid': _('expiry date not valid'),
    'Problem with bank account data.': _('Problem with bank account data.'),
    'Problem with 3d secure data.': _('Problem with 3d secure data.'),
    'currency / amount mismatch': _('currency / amount mismatch'),
    'Problem with input data.': _('Problem with input data.'),
    'Amount too low or zero.': _('Amount too low or zero.'),
    'Usage field too long.': _('Usage field too long.'),
    'Currency not allowed.': _('Currency not allowed.'),
    'General problem with backend.': _('General problem with backend.'),
    'country blacklisted.': _('country blacklisted.'),
    'Technical error with credit card.': _('Technical error with credit card.'),
    'Error limit exceeded.': _('Error limit exceeded.'),
    'Card declined by authorization system.': _('Card declined by authorization system.'),
    'Manipulation or stolen card.': _('Manipulation or stolen card.'),
    'Card restricted.': _('Card restricted.'),
    'Invalid card configuration data.': _('Invalid card configuration data.'),
    'Technical error with bank account.': _('Technical error with bank account.'),
    'Card blacklisted.': _('Card blacklisted.'),
    'Technical error with 3D secure.': _('Technical error with 3D secure.'),
    'Decline because of risk issues.': _('Decline because of risk issues.'),
    'Amount to high': _('Amount to high')
}

# -- HTML Templates for success/error OpenERP response
HTML_ERROR_RESPONSE = """
<html>
<head>
<title>OpenERP</title>
<link rel="stylesheet" type="text/css" href="./static/src/css/paymill.css">
</head>
<body class="paymill_body">
<div class="paymill_image">
    <div class="error">%s</div>
</div>
</body>
<html>
"""

HTML_SUCCESS_RESPONSE = """
<html>
<head>
<title>OpenERP</title>
<link rel="stylesheet" type="text/css" href="./static/src/css/paymill.css">
</head>
<body class="paymill_body">
<div class="paymill_image">
    <div class="success">%s</div>
</div>
</body>
<html>
"""

################################## Part-1: Setup Paymill ##################################

def __setup_paymill(self, cr, uid):
    paymill_key = get_paymill_key(self, cr, uid)
    return pymill.Pymill(paymill_key)

def update_paymill_keys(self, cr, uid, args, context=None):
    _logger.info(' ------ -- Method Call update_paymill_keys started... Arguments %s...' % str(args))
    
    ir_config_dao = self.pool.get('ir.config_parameter')

    private_key_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'paymill', PAYMILL_PRIVATE_KEY_XML_ID)[1]
    public_key_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'paymill', PAYMILL_PUBLIC_KEY_XML_ID)[1]

    ir_config_dao.write(cr, uid, private_key_id, {'value': args.get('private_key','')})
    ir_config_dao.write(cr, uid, public_key_id, {'value': args.get('public_key','')})

    _logger.info(' ------ ---- Paymill keys are updated successfully! \n Arguments --> %s ' % str(args))

    _logger.info(' ------ -- Method Call update_paymill_keys is Finished. Arguments %s.' % str(args))

def get_paymill_key(self, cr, uid):
    res_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'paymill', PAYMILL_PRIVATE_KEY_XML_ID)[1]

    return self.pool.get('ir.config_parameter').browse(cr, uid, res_id).value

def get_paymill_account_journal(self, cr, uid):
    paymill_config = self.pool.get('paymill.connect.configuration')
    config_ids = paymill_config.search(cr, uid, [])

    return paymill_config.browse(cr, uid, config_ids[0]).journal_id.id


################################## Part-2: Error Processing ##################################

def _get_translated_phrase(self, cr, uid, message):
    if message in PAYMILL_RESPONSE_ERRORS.keys():
        return PAYMILL_RESPONSE_ERRORS[message]
    
    if 'field' in message and message['field'] == 'amount' and 'messages' in message and 'notDigits' in message['messages']:
        return _('Field amount must contain only digits!')

    return message

def __process_response_codes(paymill, response_code):
    # - Handling response codes from transaction
    if response_code not in ALLOWED_RESPONSE_CODES:
        message = paymill.response_code2text(response_code)['error']
        if message in PAYMILL_RESPONSE_ERRORS.keys():
            message = PAYMILL_RESPONSE_ERRORS[message]

        raise osv.except_osv(_('Error'), _(message))


################################## Part-3: Execution of Transactions ###################################

def execute_transaction(self, cr, uid, ids, data, signal, context=None):
    try:
        paymill = __setup_paymill(self, cr, uid)

        if signal == PAYMILL_PAYMENT_TRANSACTION:
            # Invoice payment with preauthorization.
            if data.get('preauth_active', False):
                transaction = paymill.transact(
                    amount = data.get('amount',0),
                    currency = data.get('currency',''),
                    description = data.get('description',''),
                    preauth = data.get('preauth',''),
                )

            # Invoice payment without preauthorization (regular payment).                   
            else:
                transaction = paymill.transact(
                    amount = data.get('amount',0),
                    currency = data.get('currency',''),
                    description = data.get('description',''),
                    payment = data.get('payment',''),
                )

            __process_response_codes(paymill, transaction.response_code)

            return transaction

        elif signal == PAYMILL_REFUND_TRANSACTION:
            refund = paymill.refund(
                transaction_id = data.get('transaction_id',''),
                amount = data.get('amount',0),
                description = data.get('description',''),
            )

            __process_response_codes(paymill, refund.response_code)

            return refund

        elif signal == PAYMILL_PREAUTH_TRANSACTION:
            transaction = paymill.preauthorize(
                amount = data.get('amount',0),
                currency = data.get('currency',''),
                description = data.get('description',''),
                payment = data.get('payment',''),
            )

            __process_response_codes(paymill, transaction.response_code)

            return transaction

        elif signal == PAYMILL_CHECK_PREAUTH:
            transaction = paymill.get_preauthorization(preauthorization_id = data.get('preauthorization_id',''))

            return transaction

        elif signal == PAYMILL_NEW_CARD:
            transaction = paymill.new_card(
                token = data.get('token',''),
            )

            return transaction

    except Exception as ex:
        raise osv.except_osv(_('Error!'), _(_get_translated_phrase(self, cr, uid, ex.message.get('error','Unexpected Error!'))))
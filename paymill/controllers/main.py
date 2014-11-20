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

import openerp.addons.web.http as openerpweb
import openerp.addons.web.http as http
from openerp import SUPERUSER_ID
import pooler
import httplib2
from urllib import urlencode
import json
from ..paymill_config import PAYMILL_CONNECT_URL, PAYMILL_CONNECT_GRANT_TYPE, PAYMILL_CONNECT_HTTP_METHOD, PAYMILL_CONNECT_HTTP_HEADER_CONTENT_TYPE, HTML_SUCCESS_RESPONSE, HTML_ERROR_RESPONSE 

_logger = logging.getLogger(__name__)

class PAYMILL(openerpweb.Controller):
    _cp_path = "/paymill"

    @openerpweb.jsonrequest
    def get_paymill_payment_object(self, req, token):
        args = {}

        args.update({
            'token': token
        })

        result = req.session.proxy('paymill').get_paymill_payment_object(req.session._db, req.session._uid, req.session._password, args)

        return result

    @openerpweb.jsonrequest
    def get_paymill_public_key(self, req):
        args = {}

        result = req.session.proxy('paymill').get_paymill_public_key(req.session._db, req.session._uid, req.session._password, args)

        return result

    @http.httprequest
    def paymill_auth(self, request, code, **params):
        _logger.info('Configuring Paymill Keys through Paymill Connect Add-on is started...!')

        _logger.info('Part I : Paymill Connect Authentication')

        _logger.info(' - Paymill autehnticate initiated. Initial code: "%s"' % (code))
        if not code:
            _logger.error(' - Paymill autehnticate failed. No code provided')
            return HTML_ERROR_RESPONSE % 'Failure! <br/> Paymill autehnticate failed. No code provided.'

        db_name = params.get('custom_param','')
        if not db_name:
            _logger.error(' - Paymill autehnticate failed. No database name provided')
            return HTML_ERROR_RESPONSE % 'Failure! <br/> Paymill autehnticate failed. No database name provided.'

        try:
            pool = pooler.get_pool(db_name)
        except Exception as ex:
            return HTML_ERROR_RESPONSE % ('Failure! <br/> %s' % str(ex))

        cr = pool.db.cursor()

        h = httplib2.Http()
        try:
            config = pool.get('paymill.connect.configuration').get_authenticate_config(cr, SUPERUSER_ID, {})

            data = dict(
                grant_type=PAYMILL_CONNECT_GRANT_TYPE,
                scope=config.get('scope',''),
                code=code, 
                client_id=config.get('client_id',''),
                client_secret=config.get('client_secret',''),
            )

            _logger.error(' - Paymill code authentication started with following data --> %s' %  str(data))

            resp, content = h.request(PAYMILL_CONNECT_URL, PAYMILL_CONNECT_HTTP_METHOD, urlencode(data), headers={'content-type':PAYMILL_CONNECT_HTTP_HEADER_CONTENT_TYPE})

        except Exception, ex:
            _logger.error(' - Paymill code authentication failed.  More detail:%s' %  str(ex))

            return HTML_ERROR_RESPONSE % ('Failure! <br/> Paymill code authentication failed.  More detail: %s' %  str(ex))

        _logger.info(' - Paymill Connect Authentication has finished. Details: "%s", Response:"%s"' % (content, resp))

        _logger.info('Part II : Saving Paymill Authentication result into OpenERP.')

        try:
            _logger.info('Check for Paymill authentication is valid or not... Details: "%s", Response:"%s"' % (content, resp))

            if isinstance(content, str):
                content = json.loads(content)     

            # Invalid Paymill authentication
            if 'error' in content:
                _logger.info(' -- Paymill authentication is not valid...')

                error = content.get('error',''),
                error_description = content.get('error_description','')

                args = {
                    'error': error,
                    'error_description': error_description
                }

                _logger.info(' ---- Saving NOT VALID authentication details into openerp. Details %s...' % str(args))

                pool.get('paymill.connect.configuration').update_paymill_connect_configuration(cr, SUPERUSER_ID, args)

                cr.commit()

                cr.close()

                return HTML_ERROR_RESPONSE % ('Failure! <br/> Details: \n Error: %s <br/> Error Description %s' % (error, error_description))

            _logger.info('-- Paymill authentication IS VALID. Details: "%s", Response:"%s"' % (content, resp))

            _logger.info(' ---- Saving VALID Paymill authenticate details into OpenERP...')

            access_keys = content['access_keys']
            currencies = content['currencies']
            cards = content['methods']
            refresh_token = content['refresh_token']
            if 'live' in access_keys:
                keys = access_keys['live']
                live_mode = True
                test_mode = False
            else:
                keys = access_keys['test']
                live_mode = False
                test_mode = True
    
            args = {
                'private_key': keys['private_key'],
                'public_key': keys['public_key'],
                'live_mode': live_mode,
                'test_mode': test_mode,
                'currencies': currencies,
                'cards': cards,
                'refresh_token': refresh_token,
                'is_initialized': True
            }

            _logger.info(' ---- Saving following Arguments into OpenERP --> %s' % str(args))

            pool.get('paymill.connect.configuration').update_paymill_connect_configuration(cr, SUPERUSER_ID, args)
            
            cr.commit()

            cr.close()

            _logger.info(' ---- Saving VALID Paymill authenticate details into OpenERP has finished successfully. Details: %s ' % str(args))
            
            return HTML_SUCCESS_RESPONSE % 'You have successfully configured OpenERP Application for Paymill Service!'

        except Exception, ex:
            _logger.info('Unexpected error occurred. \n Details: %s' % str(ex))

            return HTML_ERROR_RESPONSE % ('Failure! <br/> Unexpected error occurred. <br/> Details: %s' % str(ex))

        _logger.info('Configuring Paymill Keys through Paymill Connect Add-on is successfully finished!')
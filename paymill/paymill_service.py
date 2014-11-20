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

import openerp
import openerp.netsvc as netsvc

_logger = logging.getLogger(__name__)

class paymill(netsvc.ExportService):

    def __init__(self, name="paymill"):
        netsvc.ExportService.__init__(self, name)

    def _process_dispatch(self, db_name, method_name, model, *method_args):
        try:
            registry = openerp.modules.registry.RegistryManager.get(db_name)
            assert registry, 'Unknown database %s' % db_name
            edi = registry[model]
            cr = registry.db.cursor()
            res = None
            res = getattr(edi, method_name)(cr, *method_args)
            cr.commit()
        except Exception:
            _logger.exception('Failed to execute PAYMILL method %s with args %r.', method_name, method_args)
            raise
        finally:
            cr.close()
        return res

    def exp_get_paymill_payment_object(self, db_name, uid, passwd, args, context=None):
        return self._process_dispatch(db_name, 'get_paymill_payment_object', 'paymill.payment.information', uid, args, context)

    def exp_get_paymill_public_key(self, db_name, uid, passwd, args, context=None):
        return self._process_dispatch(db_name, 'get_paymill_public_key', 'ir.config_parameter', uid, args, context)

    def dispatch(self, method, params):
        if method in ['get_paymill_payment_object','get_paymill_public_key']:
            (db, uid, passwd ) = params[0:3]
            openerp.service.security.check(db, uid, passwd)
        else:
            raise KeyError("Method not found: %s." % method)
        fn = getattr(self, 'exp_'+method)
        return fn(*params)

paymill()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

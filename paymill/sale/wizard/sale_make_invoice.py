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

from openerp.osv import orm, osv
from openerp.tools.translate import _

class sale_make_invoice(orm.TransientModel):
    _inherit = 'sale.make.invoice'
    
    def make_invoices(self, cr, uid, ids, context=None):        
        if type(context) is dict and context.has_key('active_ids'):
            preauth_so = []
            for sale_order in self.pool.get(context.get('active_model')).browse(cr, uid, context.get('active_ids')):
                if sale_order.paymill_preauthorization_id:
                    preauth_so.append(sale_order.name)
        
            if len(preauth_so):
                raise osv.except_osv(_('Warning!'),_('Invoice grouping is not allowed if one of Sale Orders has Paymill preauthorization! \n Following Sale Orders has preauthorizations: \n %s' % ('\n'.join(preauth_so))))
        
        return super(sale_make_invoice,self).make_invoices(cr, uid, ids, context)
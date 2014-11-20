##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, osv
from openerp.tools.translate import _

class sale_advance_payment_inv(orm.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self, cr, uid, ids, context=None):
        if type(context) is dict and context.has_key('active_id') and self.pool.get(context.get('active_model')).browse(cr, uid, context.get('active_id')).paymill_preauthorization_id and self.browse(cr, uid, ids[0]).advance_payment_method != 'all':
            raise osv.except_osv(_('Warning!'),_('This Sale Order has Paymill preauthorization and it is allowed to invoice only the whole sales order.'))
            
        return super(sale_advance_payment_inv,self).create_invoices(cr, uid, ids, context)
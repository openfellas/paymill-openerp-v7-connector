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

from openerp.osv import fields, orm

class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'is_paymill_preauth': fields.boolean('Is Preauthorization'),
        'paymill_preauthorization_id': fields.many2one('paymill.transaction', 'Paymill Preauthorization'), # This is paymill transaction object witch store info about preath
        'paymill_enable': fields.boolean('Paymill Enable')
    }

    _defaults = {
        'is_paymill_preauth': False,
        'paymill_enable': False
    }

    def action_button_confirm(self, cr, uid, ids, context=None):
        paymill_config = self.pool.get('paymill.connect.configuration')
        config_ids = paymill_config.search(cr, uid, [])

        if config_ids:
            order_currency_id = self.browse(cr, uid, ids[0]).pricelist_id.currency_id.id
            paymill_currency_ids = []
            for holder in paymill_config.browse(cr, uid, config_ids[0]).paymill_currency_holder_ids:
                paymill_currency_ids.append(holder.currency_id.id)

            if order_currency_id in paymill_currency_ids:
                self.write(cr, uid, ids, {'paymill_enable': True})

        return super(sale_order, self).action_button_confirm(cr, uid, ids, context)
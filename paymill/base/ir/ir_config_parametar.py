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

from openerp.osv import orm
from openerp.addons.paymill.paymill_config import PAYMILL_PUBLIC_KEY_XML_ID

class ir_config_parameter(orm.Model):
    _inherit = 'ir.config_parameter'

    def get_paymill_public_key(self, cr, uid, args, context=None):
        res_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'paymill', PAYMILL_PUBLIC_KEY_XML_ID)[1]
    
        return {
            'paymill_public_key': self.pool.get('ir.config_parameter').browse(cr, uid, res_id).value
        }
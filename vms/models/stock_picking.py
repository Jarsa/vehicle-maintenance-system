# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    order_line_id = fields.Many2one(
        'vms.order.line', string='Task',
    )

# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    vms_product_line_id = fields.Many2one(
        'vms.product.line', string='VMS Product Line', readonly=True,)
    vms_order_line_id = fields.Many2one(
        'vms.order.line', string='VMS Order Line',
        readonly=True, related='vms_product_line_id.order_line_id',
        store=True,)

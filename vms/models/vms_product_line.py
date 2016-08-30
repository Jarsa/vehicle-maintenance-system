# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class VmsProductLine(models.Model):
    _description = 'VMS Product Lines'
    _name = 'vms.product.line'

    product_id = fields.Many2one(
        'product.product',
        required=True,
        string='Spare Part')
    product_qty = fields.Float(
        required=True,
        default=0.0,
        string='Quantity',
        )
    product_uom_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        required=True,
        )
    task_id = fields.Many2one(
        'vms.task',
        string='Task',
        )
    order_line_id = fields.Many2one(
        'vms.order',
        string='Activity')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released')],
        readonly=True, default='draft')
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class VmsProductLine(models.Model):
    _description = 'VMS Product Lines'
    _name = 'vms.product.line'

    product_id = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'product')],
        required=True,
        string='Spare Part')
    product_qty = fields.Float(
        required=True,
        default=0.0,
        string='Quantity')
    task_id = fields.Many2one(
        'vms.task',
        string='Task')
    order_line_id = fields.Many2one(
        'vms.order',
        string='Activity')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released')],
        string='State',
        readonly=True)
    stock_move_id = fields.Many2one(
        'stock.move',
        'Stock move reference.',
        readonly=True)

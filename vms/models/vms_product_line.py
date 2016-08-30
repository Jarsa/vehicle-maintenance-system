# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import _, api, exceptions, fields, models


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
    product_uom_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        required=True)
    task_id = fields.Many2one(
        'vms.task',
        string='Task')
    order_line_id = fields.Many2one(
        'vms.order',
        string='Activity')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('cancel', 'Cancelled'),
         ('released', 'Released')],
        readonly=True, default='draft')
    stock_picking_id = fields.Many2one(
        'stock.picking',
        string='Stock Picking',
        readonly=True)

    @api.multi
    def create_stock_picking(self, location_id, product_id, product_uom_id):
        for rec in self:
            today = datetime.today.now()
            seller_id = [x[0] for x in rec.product_id.seller_ids]
            date_expected = today.timedelta(seller_id.delay)
            move = (0, 0, {
                'company_id': rec.order_line_id.order_id,
                'date': datetime.today.now(),
                'date_expected': date_expected,
                'location_dest_id': rec.order_line_id.stock_location_id.id,
                'location_id': location_id,
                'name': rec.order_line_id.name + '-' + rec.product_id.name,
                'product_id': product_id,
                'product_uom': product_uom_id,
                })
            picking = {
                'company_id': rec.order_line_id.order_id,
                'invoice_state': 'none',
                'move_type': 'one',
                'move_lines': [move],
                'type': 'in',
            }
            rec.stock_picking_id.create(picking)

    @api.multi
    def compute_state(self):
        for rec in self:
            if rec.stock_picking_id.state == 'done':
                rec.state = 'released'
            elif rec.stock_picking_id == 'cancel':
                rec.state = 'cancel'

    @api.multi
    def action_cancel(self):
        for rec in self:
            for stock in rec.stock_picking_id:
                if stock.state == 'done':
                    raise exceptions.ValidationError(
                        _('Warning! The stock'
                          'picking is already delivered'))
                else:
                    stock.state = 'cancel'
            rec.state = 'cancel'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

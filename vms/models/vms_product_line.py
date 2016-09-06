# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from datetime import timedelta
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
        'vms.order.line',
        string='Activity')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released'),
         ('cancel', 'Cancel')],
        readonly=True, default='draft')
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True)

    @api.multi
    def create_stock_picking(self, location_id, product_id,
                             product_qty, product_uom_id):
        import ipdb; ipdb.set_trace()
        for rec in self:
            stock_picking = self.env['stock.picking']
            stock_move = self.env['stock.move']
            today = datetime.strptime(fields.Datetime.now(),
                                      "%Y-%m-%d %H:%M:%S")
            seller_ids = [x[0] for x in rec.product_id.seller_ids]
            if len(seller_ids) >= 1:
                seller_id = seller_ids[0]
                date_expected = today + timedelta(days=seller_id.delay)
            else:
                date_expected = today
            move = {
                'name': str(rec.order_line_id.name) + '-' + rec.product_id.name,
                'product_id': product_id,
                'date': fields.Datetime.now(),
                'date_expected': date_expected,
                'product_uom': product_uom_id,
                'product_uom_qty': product_qty,
                'location_id': location_id,
                'location_dest_id': rec.order_line_id.stock_location_id.id,
                'picking_id': stock_picking.id,
            }
            stock_id = stock_move.create(move)
            stock_picking.move_lines += stock_id
            values = {
                'stock_move_id': stock_id.id
            }
            self.write(values)

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

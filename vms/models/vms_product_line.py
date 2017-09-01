# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, api, fields, models


class VmsProductLine(models.Model):
    _description = 'VMS Product Lines'
    _name = 'vms.product.line'

    product_id = fields.Many2one(
        'product.product',
        domain=[('type', 'in', ('product', 'consu'))],
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
         ('pending', 'Pending'),
         ('delievered', 'Delievered'),
         ('cancel', 'Cancel')],
        readonly=True, default='draft')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

    @api.multi
    def _create_stock_picking(self):
        moves = []
        picking_locations = []
        picking_dest_locations = []
        operating_units = []
        for rec in self:
            today = fields.Datetime.now()
            move = (0, 0, {
                'company_id': self.env.user.company_id.id,
                'date': today,
                'location_dest_id': (
                    rec.product_id.property_stock_production.id),
                'location_id': (
                    rec.order_line_id.order_id.stock_location_id.id),
                'name': (
                    rec.order_line_id.task_id.name +
                    '-' + rec.product_id.name),
                'product_id': rec.product_id.id,
                'product_uom': rec.product_uom_id.id,
                'product_uom_qty': rec.product_qty,
                'operating_unit_id': rec.order_id.operating_unit_id.id,
            })
            picking_locations.append(
                rec.order_line_id.order_id.stock_location_id.id)
            picking_dest_locations.append(
                rec.product_id.property_stock_production.id)
            operating_units.append(rec.operating_unit_id.id)
            moves.append(move)

        if len(set(picking_locations)) > 1:
            raise exceptions.ValidationError(_(
                'All the source locations must be equal.'))
        elif len(set(picking_dest_locations)) > 1:
            raise exceptions.ValidationError(_(
                'All the destionation locations must be equal.'))
        elif len(set(operating_units)) > 1:
            raise exceptions.ValidationError(_(
                'All the operating units must be equal.'))
        picking = {
            'company_id': self.env.user.company_id.id,
            'move_lines': [x for x in moves],
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': picking_locations[0],
            'location_dest_id': picking_dest_locations[0],
            'operating_unit_id': operating_units[0],
        }
        pick = self.env['stock.picking'].create(picking)
        return pick

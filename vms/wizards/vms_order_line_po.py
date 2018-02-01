# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class VmsOrderLinePo(models.TransientModel):
    _name = 'vms.order.line.po.wizard'

    partner_id = fields.Many2one(
        'res.partner', string='Supplier')

    @api.model
    def _prepare_item(self, line):
        return {
            'product_id': line.product_id.id,
            'product_qty': line.qty_product,
            'date_planned': fields.Datetime.now(),
            'product_uom': line.product_id.uom_po_id.id,
            'price_unit': line.product_id.standard_price,
            'taxes_id': [(
                6, 0,
                [x.id for x in (
                    line.product_id.supplier_taxes_id)]
            )],
            'name': line.product_id.name
        }

    @api.multi
    def make_po(self):
        orders = self.env['vms.order'].browse(
            self._context.get('active_ids'))
        for order in orders:
            items = []
            obj = order.order_line_ids
            lines = obj.filtered(lambda r: r.external)
            for line in lines:
                items.append((0, 0, self._prepare_item(line)))
            purchase_order_id = lines.env['purchase.order'].create({
                'partner_id': self.partner_id.id,
                'partner_ref': order.name,
                'order_line': items,
                'picking_type_id': self.env.ref(
                    'vms.stock_picking_type_vms_in').id,
            })
        lines.write({'purchase_order_id': purchase_order_id.id})
        return {
            'name': 'Purchase Order',
            'view_id': self.env.ref(
                'purchase.purchase_order_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order_id.id,
            'type': 'ir.actions.act_window'
        }

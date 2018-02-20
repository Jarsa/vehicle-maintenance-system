# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
    procurement_ids = fields.One2many(
        'procurement.order',
        'vms_product_line_id',
        string='Procurement Orders',)
    external_spare_parts = fields.Boolean(
        string='Is External Spare Part?',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        order = self.order_line_id.order_id
        prod_loc_id = (
            order.warehouse_id.wh_vms_out_picking_type_id.
            default_location_dest_id
        )
        return {
            'name': self.product_id.name,
            'origin': order.name,
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom': self.product_uom_id.id,
            'company_id': self.env.user.company_id.id,
            'group_id': group_id,
            'vms_product_line_id': self.id,
            'date_planned': fields.Datetime.now(),
            'location_id': prod_loc_id.id,
            'route_ids': self.product_id.route_ids and [
                (4, self.product_id.route_ids.ids)] or [],
            'warehouse_id': order.warehouse_id.id,
        }

    @api.multi
    def procurement_create(self):
        new_procs = self.env['procurement.order']
        proc_group_obj = self.env["procurement.group"]
        for line in self.filtered(lambda x: not x.external_spare_parts):
            if (line.order_line_id.state != 'process' or not
                    line.product_id._need_procurement()):
                continue
            qty = 0.0
            for procurement in line.procurement_ids:
                qty += procurement.product_qty

            if not line.order_line_id.order_id.procurement_group_id:
                vals = line.order_line_id.order_id._prepare_procurement_group()
                line.order_line_id.order_id.procurement_group_id = (
                    proc_group_obj.create(vals)
                )
            vals = line._prepare_order_line_procurement(
                line.order_line_id.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_qty - qty
            new_proc = self.env["procurement.order"].with_context(
                procurement_autorun_defer=True).create(vals)
            new_procs += new_proc
        new_procs.run()
        return new_procs

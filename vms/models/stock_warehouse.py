# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    wh_vms_out_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='VMS OUT Picking Operation',)

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'delivery_steps' in vals.keys():
                vms_out_operation_id = self.env.ref(
                    'vms.stock_picking_type_vms_out')
                vals.update({
                    'wh_vms_out_picking_type_id': vms_out_operation_id.id,
                })
                res = super(StockWarehouse, rec).write(vals)
                rec.get_routes_dict()
                return res
            return super(StockWarehouse, rec).write(vals)

    def get_routes_dict(self):
        res = super(StockWarehouse, self).get_routes_dict()
        stock_loc_obj = self.env['stock.location']
        prod_loc = stock_loc_obj.search(
            [('usage', '=', 'production')], limit=1)
        for warehouse in self.browse(res.keys()):
            res[warehouse.id]['ship_only'].append(
                self.Routing(
                    warehouse.lot_stock_id,
                    prod_loc,
                    warehouse.wh_vms_out_picking_type_id))
        return res

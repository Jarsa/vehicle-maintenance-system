# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_compare


class VmsProductLine(models.Model):
    _description = "VMS Product Lines"
    _name = "vms.product.line"

    product_id = fields.Many2one(
        "product.product",
        domain=[("type", "in", ("product", "consu"))],
        required=True,
        string="Spare Part",
    )
    product_qty = fields.Float(
        required=True,
        default=1.0,
        string="Quantity",
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        required=True,
    )
    task_id = fields.Many2one("vms.task")
    order_line_id = fields.Many2one(
        "vms.order.line",
        string="Activity",
        ondelete="cascade",
    )
    order_id = fields.Many2one(related="order_line_id.order_id")
    company_id = fields.Many2one(related="order_line_id.company_id", store=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        vms.product.line. procurement group will launch '_run_pull', '_run_buy' or
        '_run_manufacture' depending on the sale order line product rule.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.product_id.type not in ("consu", "product"):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if (
                float_compare(qty, line.product_uom_qty, precision_digits=precision)
                == 0
            ):
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env["procurement.group"].create(
                    line._prepare_procurement_group_vals()
                )
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_id:
                    updated_vals.update({"partner_id": line.order_id.partner_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({"move_type": line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_qty - qty

            line_uom = line.product_uom_id
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                product_qty, quant_uom
            )
            procurements.append(
                self.env["procurement.group"].Procurement(
                    line.product_id,
                    product_qty,
                    procurement_uom,
                    line.product_id.property_stock_production,
                    line.name,
                    line.order_id.name,
                    line.order_id.company_id,
                    values,
                )
            )
        if procurements:
            self.env["procurement.group"].run(procurements)

        # This next block is currently needed only because the scheduler trigger is done
        #  by picking confirmation rather than stock.move confirmation
        orders = self.mapped("order_id")
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(
                lambda p: p.state not in ["cancel", "done"]
            )
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return True

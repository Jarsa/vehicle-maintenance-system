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
    name = fields.Char(string="Description", required=True)
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
    move_ids = fields.One2many(
        "stock.move", "vms_product_line_id", string="Stock Moves"
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain=[("vms_selectable", "=", True)],
        ondelete="restrict",
        check_company=True,
    )
    company_id = fields.Many2one(related="order_line_id.company_id", store=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.update(
            {
                "name": self.product_id.display_name,
                "product_uom_id": self.product_id.uom_id.id,
            }
        )

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        vms.product.line. procurement group will launch "_run_pull", "_run_buy" or
        "_run_manufacture" depending on the sale order line product rule.
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
            if float_compare(qty, line.product_qty, precision_digits=precision) == 0:
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

    def _get_qty_procurement(self, previous_product_uom_qty=False):
        self.ensure_one()
        qty = 0.0
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom, rounding_method="HALF-UP"
            )
        for move in incoming_moves:
            qty -= move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom, rounding_method="HALF-UP"
            )
        return qty

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env["stock.move"]
        incoming_moves = self.env["stock.move"]

        moves = self.move_ids.filtered(
            lambda r: r.state != "cancel"
            and not r.scrapped
            and self.product_id == r.product_id
        )

        for move in moves:
            if move.location_dest_id.usage == "production":
                if not move.origin_returned_move_id or (
                    move.origin_returned_move_id and move.to_refund
                ):
                    outgoing_moves |= move
            elif move.location_dest_id.usage != "production" and move.to_refund:
                incoming_moves |= move

        return outgoing_moves, incoming_moves

    def _get_procurement_group(self):
        return self.order_id.procurement_group_id

    def _prepare_procurement_group_vals(self):
        return {
            "name": self.order_id.name,
            "move_type": self.order_id.picking_policy,
            "vms_order_id": self.order_id.id,
            "partner_id": self.order_id.partner_id.id,
        }

    def _prepare_procurement_values(self, group_id=False):
        """Prepare specific key for moves or other components that will be created from
        a stock rule comming from a vms.product.line. This method could be override in
        order to add other custom key that could
        be used in move/po creation.
        """
        self.ensure_one()
        return {
            "group_id": group_id,
            "vms_product_line_id": self.id,
            "date_planned": self.order_id.start_date or self.order_id.date,
            "date_deadline": self.order_id.end_date,
            "route_ids": self.route_id,
            "warehouse_id": self.order_id.warehouse_id or False,
            "partner_id": self.order_id.partner_id.id,
            "company_id": self.order_id.company_id,
        }

# Copyright 2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
    )
    vms_order_ids = fields.One2many(
        comodel_name="vms.order",
        inverse_name="sale_order_id",
    )
    vms_order_count = fields.Integer(
        compute="_compute_vms_order_count",
    )

    def _compute_vms_order_count(self):
        for rec in self:
            rec.vms_order_count = len(rec.vms_order_ids)

    def action_view_vms_orders(self):
        self.ensure_one()
        orders = self.mapped("vms_order_ids")
        action = self.env["ir.actions.actions"]._for_xml_id("vms.action_vms_order")
        if len(orders) > 1:
            action["domain"] = [("id", "in", orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref("vms.vms_order_form_view").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = orders.id
        return action

    def _action_confirm(self):
        res = super()._action_confirm()
        for rec in self:
            rec.sudo().with_company(rec.company_id)._create_vms_order()
        return res

    def _create_vms_order(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda sol: sol.product_id.vms_service_tracking
            in ["preventive", "corrective"]
        )
        if lines and not self.vehicle_id:
            raise UserError(_("You must select a vehicle to create a VMS order."))
        for line in lines:
            self.env["vms.order"].sudo().create(
                {
                    "type": line.product_id.vms_service_tracking,
                    "sale_order_id": self.id,
                    "sale_order_line_id": line.id,
                    "company_id": self.company_id.id,
                    "warehouse_id": self.warehouse_id.id,
                    "partner_id": self.partner_id.commercial_partner_id.id,
                    "program_id": line.program_id.id,
                    "vehicle_id": self.vehicle_id.id,
                }
            )
        return True

    def _action_cancel(self):
        for rec in self:
            if rec.vms_order_ids:
                rec.vms_order_ids.action_cancel()
        return super()._action_cancel()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    program_id = fields.Many2one(
        related="order_id.vehicle_id.model_id.program_id",
        string="Maintenance Plan",
        store=True,
    )
    cycle_ids = fields.Many2many(
        related="program_id.cycle_ids",
        string="Maintenance Cycles",
    )
    cycle_id = fields.Many2one(
        comodel_name="vms.cycle",
        string="Maintenance Cycle",
    )
    vms_service_tracking = fields.Selection(
        related="product_id.vms_service_tracking",
        string="VMS Service Tracking",
    )

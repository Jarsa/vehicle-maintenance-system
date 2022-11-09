# Copyright 2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsOrder(models.Model):
    _inherit = "vms.order"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        readonly=True,
        copy=False,
    )
    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        readonly=True,
        copy=False,
    )

    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["res_id"] = self.sale_order_id.id
        form_view = [(self.env.ref("sale.view_order_form").id, "form")]
        if "views" in action:
            action["views"] = form_view + [
                (state, view) for state, view in action["views"] if view != "form"
            ]
        else:
            action["views"] = form_view
        return action

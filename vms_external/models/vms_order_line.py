# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrderLine(models.Model):
    _inherit = "vms.order.line"

    external = fields.Boolean()
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order", readonly=True
    )
    create_purchase_order = fields.Boolean(compute="_compute_create_purchase_order")

    @api.depends("purchase_order_id")
    def _compute_purchase_state(self):
        for rec in self:
            rec.purchase_state = (
                rec.purchase_order_id.id and rec.purchase_order_id.state == "done"
            )

    @api.onchange("external")
    def _onchange_external(self):
        for rec in self:
            spare_part_ids = [(5, 0, 0)]
            if not rec.external:
                for spare_part in self.task_id.spare_part_ids:
                    spare_part_ids.append(
                        (0, 0, self._prepare_spare_part_ids(spare_part))
                    )
            rec.update(
                {
                    "spare_part_ids": spare_part_ids,
                }
            )

    @api.depends("spare_part_ids")
    def _compute_create_purchase_order(self):
        for rec in self:
            rec.create_purchase_order = bool(
                rec.spare_part_ids.filtered(lambda x: x.external_spare_parts)
            )

    def action_done(self):
        for rec in self:
            if (
                rec.external
                and rec.purchase_order_id
                and rec.purchase_order_id.state not in ("done", "purchase")
            ):
                raise ValidationError(
                    _("Purchase Order %s is not done") % rec.purchase_order_id.name
                )
        return super().action_done()

    def _prepare_purchase_order(self):
        self.ensre_one()
        return {
            "partner_id": self.supplier_id.id,
            "partner_ref": self.order_id.name,
            "order_line": self._prepare_purchase_order_lines(),
            "picking_type_id": self.env.ref("vms.stock_picking_type_vms_in").id,
        }

    def _prepare_purchase_order_lines(self):
        self.ensure_one()
        order_lines = []
        for line in self.spare_part_ids.filtered(lambda r: r.external_spare_parts):
            order_lines.append((0, 0, self._prepare_purchase_order_line(line)))
        return order_lines

    def _prepare_purchase_order_line(self, line):
        self.ensure_one()
        return {
            "product_id": line.product_id.id,
            "product_qty": line.product_qty,
            "date_planned": fields.Datetime.now(),
            "product_uom": line.product_id.uom_po_id.id,
            "price_unit": line.product_id.standard_price,
            "taxes_id": [(6, 0, [x.id for x in (line.product_id.supplier_taxes_id)])],
            "name": line.product_id.name,
        }

    def _action_create_purchase_order(self):
        self.ensure_one()
        purchase_order = self.env["purchase.order"].create(
            self._prepare_purchase_order()
        )
        self.write({"purchase_order_id": purchase_order.id})
        return purchase_order

    def action_create_purchase_order(self):
        orders = self.env["purchase.order"]
        for rec in self:
            orders |= rec._action_create_purchase_order()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        if len(orders) > 1:
            action["domain"] = [("id", "in", orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref("purchase.purchase_order_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = orders.id
        return action

# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class VmsReport(models.Model):
    _description = "VMS Reports"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "vms.report"

    name = fields.Char(string="Number", readonly=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    unit_id = fields.Many2one("fleet.vehicle", required=True, string="Unit")
    order_id = fields.Many2one("vms.order", readonly=True, string="Order")
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        string="Driver",
        domain=[("mechanic", "=", True)],
    )
    end_date = fields.Datetime()
    state = fields.Selection(
        [("pending", "Pending"), ("closed", "Closed"), ("cancel", "Cancel")],
        default="pending",
    )
    notes = fields.Html()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get("name", _("/")) == _("/"):
                values["name"] = self.env["ir.sequence"].next_by_code("vms.report")
        return super().create(vals_list)

    def action_confirmed(self):
        for rec in self:
            rec.state = "closed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def action_pending(self):
        for rec in self:
            rec.state = "pending"

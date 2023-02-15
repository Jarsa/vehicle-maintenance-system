# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class VmsOrder(models.Model):
    _inherit = "vms.order"

    report_ids = fields.Many2many("vms.report", string="Report(s)")
    report_count = fields.Integer(
        string="Reports",
        compute="_compute_report_count",
        copy=False,
    )

    @api.depends("report_ids")
    def _compute_report_count(self):
        for rec in self:
            rec.report_count = len(rec.report_ids)

    def action_view_reports(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "vms_report.action_vms_report"
        )
        reports = self.mapped("report_ids")
        if len(reports) > 1:
            action["domain"] = [("id", "in", reports.ids)]
        elif reports:
            action["views"] = [
                (self.env.ref("vms_report.vms_report_form_view").id, "form")
            ]
            action["res_id"] = reports.id
        return action

    def action_open(self):
        self.mapped("report_ids").write({"state": "in_progress"})
        return super().action_open()

    def action_released(self):
        self.mapped("report_ids").write({"state": "closed"})
        return super().action_released()

    def action_cancel(self):
        self.mapped("report_ids").write({"state": "pending"})
        return super().action_cancel()

    def action_cancel_draft(self):
        self.mapped("report_ids").write({"state": "pending"})
        return super().action_cancel_draft()

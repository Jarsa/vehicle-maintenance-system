# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsWizardMaintenanceOrder(models.TransientModel):
    _name = "vms.wizard.maintenance.order"
    _description = "VMS Wizard Maintenance Order"

    @api.model
    def default_get(self, default_fields):
        res = super(VmsWizardMaintenanceOrder, self).default_get(default_fields)
        report_ids = self._context.get("active_ids")
        reports = self.env["vms.report"].browse(report_ids)
        self.validate(reports)
        return res

    def _prepare_order(self, report):
        return {
            "unit_id": report.unit_id.id,
            "type": "corrective",
            "date": fields.Datetime.now(),
        }

    def make_orders(self):
        reports = self.env["vms.report"].browse(self._context.get("active_ids"))
        order_id = self.env["vms.order"].create(self._prepare_order(reports[0]))
        for record in reports:
            record.write({"order_id": order_id.id})
            order_id.write({"report_ids": [(4, record.id)]})
        message = _("<strong>Order of:</strong> %s </br>") % (
            ", ".join(reports.mapped("name"))
        )
        order_id.message_post(body=message)
        return {
            "name": "Maintenance Order",
            "view_id": self.env.ref("vms.vms_order_form_view").id,
            "view_mode": "form",
            "res_model": "vms.order",
            "res_id": order_id.id,
            "type": "ir.actions.act_window",
        }

    @api.model
    def validate(self, reports):
        if len(reports.mapped("unit_id")) > 1:
            raise ValidationError(_("All record must be of the same Unit"))
        if reports.mapped("order_id"):
            raise ValidationError(_("All least one record has an order assigned"))

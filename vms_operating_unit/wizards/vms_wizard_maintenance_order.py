# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class VmsWizardMaintenanceOrder(models.TransientModel):
    _inherit = "vms.wizard.maintenance.order"

    def _prepare_order(self, report):
        res = super()._prepare_order(report)
        res["operating_unit_id"] = report.operating_unit_id.id
        return res

    @api.model
    def validate(self, reports):
        res = super().validate(reports)
        if len(reports.mapped("operating_unit_id")) > 1:
            raise ValidationError(_("All reports must be in the same Operating Unit"))
        return res

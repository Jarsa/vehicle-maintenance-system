# Copyright 2022 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models


class VmsReport(models.Model):
    _inherit = "vms.report"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("/")) == _("/") and vals.get(
                "operating_unit_id", False
            ):
                ou_id = self.env["operating.unit"].browse(vals["operating_unit_id"])
                if ou_id.vms_report_sequence_id:
                    vals["name"] = ou_id.vms_report_sequence_id.next_by_id()
        return super().create(vals_list)

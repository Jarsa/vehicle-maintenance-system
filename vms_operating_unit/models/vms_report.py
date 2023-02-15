# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsReport(models.Model):
    _inherit = "vms.report"

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        string="Operating Unit",
        default=_default_operating_unit,
        readonly=True,
        states={"pending": [("readonly", False)]},
    )

    @api.constrains("operating_unit_id", "company_id")
    def _check_company_operating_unit(self):
        for rec in self:
            if (
                rec.company_id
                and rec.operating_unit_id
                and rec.company_id != rec.operating_unit_id.company_id
            ):
                raise ValidationError(
                    _(
                        "Configuration error. The Company in "
                        "the Report and in the Operating "
                        "Unit must be the same."
                    )
                )

# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrder(models.Model):
    _inherit = "vms.order"

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        string="Operating Unit",
        default=_default_operating_unit,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.onchange("operating_unit_id")
    def _onchange_operating_unit_id(self):
        if (
            self.warehouse_id
            and self.warehouse_id.operating_unit_id != self.operating_unit_id
        ):
            self.warehouse_id = self.env["stock.warehouse"].search(
                [("operating_unit_id", "=", self.operating_unit_id.id)], limit=1
            )

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        if (
            self.warehouse_id
            and self.warehouse_id.operating_unit_id != self.operating_unit_id
        ):
            self.operating_unit_id = self.warehouse_id.operating_unit_id

    @api.constrains("warehouse_id", "operating_unit_id")
    def _check_warehouse_operating_unit(self):
        for rec in self:
            if (
                rec.warehouse_id
                and rec.warehouse_id.operating_unit_id != rec.operating_unit_id
            ):
                raise ValidationError(
                    _(
                        "Configuration error. The Operating "
                        "Unit of the warehouse must match "
                        "with that of the order."
                    )
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
                        "the Order and in the Operating "
                        "Unit must be the same."
                    )
                )

    @api.model
    def _get_warehouse_domain(self):
        res = super()._get_warehouse_domain()
        res.append(
            ("operating_unit_id", "=", self.env.user.default_operating_unit_id.id)
        )
        return res

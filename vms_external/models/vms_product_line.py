# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsProductLine(models.Model):
    _inherit = "vms.product.line"

    external_spare_parts = fields.Boolean(
        string="Is External Spare Part?",
    )

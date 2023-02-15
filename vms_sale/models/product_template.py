# Copyright 2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    vms_service_tracking = fields.Selection(
        selection=[
            ("no", "No"),
            ("corrective", "Create a Corrective VMS Order"),
            ("preventive", "Create a Preventive VMS Order"),
        ],
        string="VMS Service Tracking",
        default="no",
    )

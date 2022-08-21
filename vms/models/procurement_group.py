# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    vms_order_id = fields.Many2one("vms.order", "VMS Order")

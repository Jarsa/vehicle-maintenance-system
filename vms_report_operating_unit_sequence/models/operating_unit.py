# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    vms_report_sequence_id = fields.Many2one("ir.sequence", string="Report Sequence")

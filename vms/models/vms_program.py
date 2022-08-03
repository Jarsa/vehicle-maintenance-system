# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsProgram(models.Model):
    _name = "vms.program"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc"
    _description = "VMS Programs"

    cycle_ids = fields.Many2many(
        "vms.cycle", required=True, string="Cycle(s)", store=True
    )
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

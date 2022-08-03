# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsCycle(models.Model):
    _name = "vms.cycle"
    _order = "name asc"
    _description = "VMS Cycle"

    name = fields.Char(required=True)
    task_ids = fields.Many2many("vms.task", string="Tasks", required=True)
    cycle_ids = fields.Many2many(
        comodel_name="vms.cycle",
        relation="vms_cycle_rel",
        column1="cycle",
        column2="other_cycle",
        string="Cycles",
    )
    frequency = fields.Integer(required=True)
    active = fields.Boolean(default=True)

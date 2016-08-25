# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class VmsCycle(models.Model):
    _name = 'vms.cycle'
    _order = 'name asc'

    name = fields.Char(required=True)
    task_ids = fields.Many2many(
        'vms.task', string='Tasks')
    # cycle_ids = fields.Many2many(
    #     'vms.cycle', string='Cycles')
    frecuency = fields.Float(
        required=True)
    active = fields.Boolean(
        default=True)

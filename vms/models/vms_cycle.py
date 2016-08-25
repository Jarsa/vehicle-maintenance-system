# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class Cycle(models.Model):
    _name = 'vms.cycle'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    task_ids = fields.Many2many(
        'vms.task')
    cycle_ids = fields.One2many(
        'vms.cycle',
        'cycle_id',)
    cycle_id = fields.Many2one(
        'vms.cycle',
        string='Cycles')
    frecuency = fields.Float(
        required=True, string='Frecuency')
    active = fields.Boolean(
        default=True, string='Is active?')

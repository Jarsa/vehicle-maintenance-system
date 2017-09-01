# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsTask(models.Model):
    _name = 'vms.task'
    _description = 'VMS Task'
    _order = 'name asc'

    name = fields.Char(required=True)
    duration = fields.Float(required=True, store=True)
    spare_part_ids = fields.One2many(
        'vms.product.line',
        'task_id', string="Spare Parts",
        store=True)
    active = fields.Boolean(default=True)

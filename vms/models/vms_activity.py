# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class VmsActivity(models.Model):
    _name = 'vms.activity'
    _order = 'order_id asc'

    name = fields.Char(required=True)
    order_id = fields.Many2one(
        'vms.order',
        required=True,
        string='Maintenance Order',
        readonly=True)
    order_line_id = fields.Many2one(
        'vms.order.line',
        required=True,
        string='Activity',
        readonly=True)
    unit_id = fields.Many2one(
        'fleet.vehicle',
        required=True,
        string='Unit',
        readonly=True)
    task_id = fields.Many2one(
        'vms.task',
        string='Task',
        readonly=True)
    responsible_id = fields.Many2one(
        'hr.employee',
        domain=[('mechanic', '=', True)],
        string='Responsible',
        readonly=True)

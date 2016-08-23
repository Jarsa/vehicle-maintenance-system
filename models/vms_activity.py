# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class Activity(models.Model):
    _name = 'vms.activity'
    _order = 'name asc'

    order_id = fields.Many2one(
        'vms.order', readonly=True, required=True)
    unit_id = fields.Many2one(
        'fleet.vehicle', readonly=True, required=True)
    total_hours = fields.Float(
        # compute=_compute_total_hours
        )
    activity_time_ids = fields.One2many(
        'vms.activity.time', 'activity_id', readonly=True)
    task_id = fields.Many2one(
        'vms.task', readonly=True)
    responsible_id = fields.Many2one(
        'hr.employee', domain=[('mechanic', '=', True)], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('pause', 'Pause'),
        ('end', 'End'),
        ('cancel', 'Cancel'),
        ], default='draft', readonly=True)
    start_date = fields.Datetime()
    end_date = fields.Datetime()

# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import _, api, fields, models


class VmsActivity(models.Model):
    _name = 'vms.activity'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'order_id asc'

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
    total_hours = fields.Float(
        compute='_compute_total_hours')
    activity_time_ids = fields.One2many(
        'vms.activity.time',
        'activity_id',
        string='Activities',
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
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('pause', 'Pause'),
        ('end', 'End'),
        ('cancel', 'Cancel'),
        ], default='draft', readonly=True)
    start_date = fields.Datetime(readonly=True)
    end_date = fields.Datetime(readonly=True)

    @api.depends('activity_time_ids')
    def calculate_diference_time(self, date_begin, date_end):
        duration = datetime.strptime(
            date_end, '%Y-%m-%d %H:%M:%S') - datetime.strptime(
            date_begin, '%Y-%m-%d %H:%M:%S')
        diference = (duration.seconds / 3600.0) + (duration.days / 24)
        return diference

    def _compute_total_hours(self):
        sum_time = 0.0
        for rec in self:
            for activity in rec.activity_time_ids:
                if activity.status in 'process':
                    temp_begin = activity.date
                elif activity.status in ('pause', 'end'):
                    sum_time += self.calculate_diference_time(
                        temp_begin, activity.date)
            total = (sum_time*60)/100
            rec.total_hours = total

    @api.multi
    def action_start(self):
        for rec in self:
            rec.order_line_id.start_date_real = rec.start_date
            rec.activity_time_ids.create({
                'status': 'process',
                'date': fields.Datetime.now(),
                'activity_id': rec.id
                })
            rec.write({
                'state': 'process',
                'start_date': fields.Datetime.now()
                })
            rec.message_post(_(
                '<strong>Activity Started.</strong><ul>'
                '<li><strong>Started by: </strong>%s</li>'
                '<li><strong>Started at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_pause(self):
        for rec in self:
            rec.activity_time_ids.create({
                'status': 'pause',
                'date': fields.Datetime.now(),
                'activity_id': rec.id
                })
            rec.write({
                'state': 'pause'
                })
            rec.message_post(_(
                '<strong>Activity Paused.</strong><ul>'
                '<li><strong>Paused by: </strong>%s</li>'
                '<li><strong>Paused at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_resume(self):
        for rec in self:
            rec.activity_time_ids.create({
                'status': 'process',
                'date': fields.Datetime.now(),
                'activity_id': rec.id
                })
            rec.write({
                'state': 'process'
                })
            rec.message_post(_(
                '<strong>Activity Resumed.</strong><ul>'
                '<li><strong>Resumed by: </strong>%s</li>'
                '<li><strong>Resumed at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
        rec.message_post(_(
            '<strong>Activity Canceled.</strong><ul>'
            '<li><strong>Canceled by: </strong>%s</li>'
            '<li><strong>Canceled at: </strong>%s</li>'
            '</ul>') % (self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_end(self):
        for rec in self:
            rec.order_line_id.end_date_real = rec.end_date
            rec.activity_time_ids.create({
                'status': 'end',
                'date': fields.Datetime.now(),
                'activity_id': rec.id
                })
            rec.write({
                'state': 'end',
                'end_date': fields.Datetime.now()
                })
            rec.message_post(_(
                '<strong>Activity Ended.</strong><ul>'
                '<li><strong>Ended by: </strong>%s</li>'
                '<li><strong>Ended at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.message_post(_(
                '<strong>Activity Drafted.</strong><ul>'
                '<li><strong>Drafted by: </strong>%s</li>'
                '<li><strong>Drafted at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

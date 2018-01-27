# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsActivity(models.Model):
    _name = 'vms.activity'
    _description = 'Mechanic Activity'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'priority desc'

    name = fields.Char(required=True)
    order_id = fields.Many2one(
        'vms.order', string='Maintenance Order', required=True, readonly=True)
    order_line_id = fields.Many2one(
        'vms.order.line', string='Activity', required=True, readonly=True)
    task_id = fields.Many2one(
        'vms.task', string='Task', readonly=True)
    responsible_id = fields.Many2one(
        'hr.employee', string='Responsible', readonly=True,
        domain=[('mechanic', '=', True)])
    unit_id = fields.Many2one(
        'fleet.vehicle', string='Unit', required=True, readonly=True)
    activity_time_ids = fields.One2many(
        'vms.activity.time', 'activity_id', string='Activities',
        readonly=True, ondelete='cascade')
    total_hours = fields.Float(compute='_compute_total_hours')
    priority = fields.Selection([
        ('0', 'All'),
        ('1', 'Low priority'),
        ('2', 'High priority'),
        ('3', 'Urgent')], default='1')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancel'),
        ('pending', 'Pending'),
        ('process', 'Process'),
        ('pause', 'Pause'),
        ('end', 'End'),
    ], default='draft', readonly=True)
    start_date = fields.Datetime(readonly=True)
    end_date = fields.Datetime(readonly=True)

    @api.depends('activity_time_ids')
    def _compute_total_hours(self):
        for rec in self:
            sum_time = 0.0
            for activity in rec.activity_time_ids.filtered(
                    lambda r: r.state == 'end'):
                start_date = fields.Datetime.from_string(activity.start_date)
                end_date = fields.Datetime.from_string(activity.end_date)
                sum_time += (end_date - start_date).total_seconds()/3600
            rec.total_hours = float("%.2f" % sum_time)

    @api.multi
    def start_end_activity_time(self, rec):
        """ Toggle action to start or end an activity. """
        act_in_process = self.end_activity_time(rec, throw_back_act=True)
        if not act_in_process:
            other_act = self.search([
                ('id', '!=', rec.id),
                ('responsible_id', '=', rec.responsible_id.id),
                ('state', '=', 'process')], limit=1)
            if other_act:
                raise ValidationError(_('There is another task in process.'))
            rec.activity_time_ids.create({
                'start_date': fields.Datetime.now(),
                'activity_id': rec.id,
                'state': 'process',
            })
            rec.state = 'process'
        else:
            rec.state = 'pause'

    @api.multi
    def end_activity_time(self, rec, throw_back_act=False):
        """ End an activityin process. """
        act_in_process = self.env['vms.activity.time'].search(
            [('activity_id', '=', rec.id), ('state', '=', 'process')],
            limit=1)
        if act_in_process:
            act_in_process.write({
                'end_date': fields.Datetime.now(),
                'state': 'end',
            })
        if throw_back_act:
            return act_in_process

    @api.multi
    def process_validations(self):
        """ Validations in case, order line or activity are not in process. """
        for rec in self:
            if rec.order_line_id.state != 'process':
                raise ValidationError(_('The order line task must be open.'))
            if rec.state in ['draft', 'end', 'cancel']:
                raise ValidationError(_(
                    'The activity must be in Pending, Process or Pause'))

    @api.multi
    def action_start(self):
        """ Change activity to process and start a new activity time. """
        for rec in self:
            self.process_validations()
            self.start_end_activity_time(rec)
            rec.start_date = fields.Datetime.now()

    @api.multi
    def action_pause(self):
        """ Pause the current activity time in process. """
        for rec in self:
            self.start_end_activity_time(rec)

    @api.multi
    def action_resume(self):
        """ Resume the activity, creates a new activity time. """
        for rec in self:
            self.process_validations()
            self.start_end_activity_time(rec)

    @api.multi
    def action_cancel(self):
        """ Cancel the activity """
        for rec in self:
            self.end_activity_time(rec)
            rec.state = 'cancel'

    @api.multi
    def action_end(self):
        """ Ends the activity and activity times. """
        for rec in self:
            self.end_activity_time(rec)
            rec.state = 'end'
            rec.end_date = fields.Datetime.now()

    @api.multi
    def action_draft(self):
        """ Sets to draft the activity. """
        for rec in self:
            self.end_activity_time(rec)
            rec.state = 'draft'

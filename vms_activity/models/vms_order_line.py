# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrderLine(models.Model):
    _inherit = 'vms.order.line'

    responsible_ids = fields.Many2many(
        'hr.employee', string='Mechanics', domain=[('mechanic', '=', True)])
    activity_ids = fields.One2many(
        'vms.activity', 'order_line_id', string="Activities",
        readonly=True, ondelete='cascade')
    priority = fields.Selection([
        ('0', 'All'),
        ('1', 'Low priority'),
        ('2', 'High priority'),
        ('3', 'Urgent')], default='0')

    @api.multi
    def action_process(self):
        """ Creates the activities by mechanic when open the Order """
        activity_obj = self.env['vms.activity']
        for rec in self:
            if not rec.external:
                if not rec.responsible_ids:
                    raise ValidationError(
                        _('The tasks must have almost one mechanic.'))
                for mechanic in rec.responsible_ids:
                    task = activity_obj.search([
                        ('order_id', '=', rec.order_id.id),
                        ('order_line_id', '=', rec.id),
                        ('task_id', '=', rec.task_id.id),
                        ('responsible_id', '=', mechanic.id)], limit=1)
                    if task:
                        task.state = 'pending'
                    else:
                        activity_obj.create({
                            'name': rec.task_id.name,
                            'order_id': rec.order_id.id,
                            'order_line_id': rec.id,
                            'task_id': rec.task_id.id,
                            'responsible_id': mechanic.id,
                            'unit_id': rec.order_id.unit_id.id,
                            'state': 'pending',
                            'priority': rec.priority,
                        })
        super(VmsOrderLine, self).action_process()

    @api.multi
    def get_real_duration(self):
        for rec in self:
            if not rec.activity_ids:
                return super(VmsOrderLine, self).get_real_duration()
            duration_sum = 0.0
            for activity in rec.activity_ids:
                if activity.state == 'end':
                    duration_sum += activity.total_hours
                else:
                    raise ValidationError(
                        _('All the activities must be finished.'))
            rec.real_duration = duration_sum

    @api.multi
    def action_cancel(self):
        for rec in self.filtered(lambda r: not r.external):
            rec.activity_ids.write({'state': 'cancel'})
        super(VmsOrderLine, self).action_cancel()

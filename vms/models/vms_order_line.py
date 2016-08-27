# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from datetime import timedelta
from openerp import api, fields, models


class VmsOrderLine(models.Model):
    _name = 'vms.order.line'
    _order = 'name asc'

    task_id = fields.Many2one(
        'vms.task', string='Task',
        required=True)
    start_date = fields.Datetime(
        default=fields.Datetime.now(),
        string='Schedule start',
        required=True)
    end_date = fields.Datetime(
        compute='_compute_end_date_',
        string='Schedule end',
        required=True)
    start_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    end_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    scheduled_hours = fields.Float(
        string='Schedule hours'
        #    compute=_compute_scheduled_hours
        )
    supplier_id = fields.Many2one(
        'res.partner',
        domain=[('supplier', '=', True)])
    external = fields.Boolean()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel')])
    real_hours = fields.Float(
        compute="_compute_real_hours",
        string="Real Hours")
    spare_part_ids = fields.One2many(
        'vms.product.line',
        'order_line_id')
    responsible_ids = fields.Many2many(
        'hr.employee',
        domain=[('mechanic', '=', True)])
    invoice_id = fields.Many2one(
        'account.invoice',
        readonly=True)
    paid = fields.Boolean(
        compute='_compute_paid'
        )
    order_id = fields.Many2one('vms.order', string='Order')
    real_time_total = fields.Integer(string='Real time total')

    @api.onchange('task_id')
    def _onchange_task(self):
        self.scheduled_hours = self.task_id.duration
        strp_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        end_date = strp_date + timedelta(hours=self.scheduled_hours)
        self.end_date = end_date

    @api.depends('start_date_real', 'end_date_real')
    def _compute_real_time_total(self):
        for rec in self:
            start_date = datetime.strptime(rec.start_date_real, '%Y-%m-%d')
            end_date = datetime.strptime(rec.end_date_real, '%Y-%m-%d')
            total_days = start_date - end_date
            rec.real_time_total = total_days.days

    @api.depends('invoice_id')
    def _compute_paid(self):
        for rec in self:
            self.paid = rec.invoice_id.state

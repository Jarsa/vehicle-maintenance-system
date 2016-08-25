# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


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
        # compute = _compute_end_date_
        string='Schedule end',
        required=True)
    start_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    end_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    scheduled_hours = fields.Float(
        string='Schedule hours'
        # compute=_compute_scheduled_hours
        )
    supplier_id = fields.Many2one(
        'res.partner',
        domain=[('supplier', '=', True)])
    external = fields.Boolean()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ], default='pending', readonly=True)
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
        # compute=_compute_paid
        )
    order_id = fields.Many2one('vms.order', string='Order')

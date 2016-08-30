# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from datetime import timedelta
from openerp import api, fields, models


class VmsOrderLine(models.Model):
    _name = 'vms.order.line'
    _description = 'VMS Order Line'

    task_id = fields.Many2one(
        'vms.task', string='Task',
        required=True)
    start_date = fields.Datetime(
        default=fields.Datetime.now(),
        string='Schedule start',
        required=True)
    end_date = fields.Datetime(
        string='Schedule end',
        required=True)
    start_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    end_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    duration = fields.Float()
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)])
    external = fields.Boolean()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel')],
        default='pending')
    real_duration = fields.Float()
    spare_part_ids = fields.One2many(
        'vms.product.line',
        'order_line_id',
        string='Spare Parts')
    responsible_ids = fields.Many2many(
        'hr.employee',
        string='Mechanics',
        domain=[('mechanic', '=', True)])
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True)

    order_id = fields.Many2one('vms.order', string='Order', readonly=True)
    real_time_total = fields.Integer()

    @api.multi
    def action_confirm(self):
        for rec in self:
            for product in rec.spare_part_ids:
                product.create_stock_picking(
                    rec.order_id.stock_location_id.id,
                    product.product_id.id,
                    product.product_uom_id)

    @api.onchange('task_id')
    def _onchange_task(self):
        self.duration = self.task_id.duration
        self.spare_part_ids = self.task_id.spare_part_ids
        strp_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        self.end_date = strp_date + timedelta(hours=self.duration)

    @api.onchange('duration')
    def _onchange_duration(self):
        strp_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        self.end_date = strp_date + timedelta(hours=self.duration)

    @api.depends('start_date_real', 'end_date_real')
    def _compute_real_time_total(self):
        for rec in self:
            start_date = datetime.strptime(rec.start_date_real, '%Y-%m-%d')
            end_date = datetime.strptime(rec.end_date_real, '%Y-%m-%d')
            total_days = start_date - end_date
            rec.real_time_total = total_days.days

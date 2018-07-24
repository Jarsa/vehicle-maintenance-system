# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrder(models.Model):
    _description = 'VMS Orders'
    _inherit = 'mail.thread'
    _name = 'vms.order'

    name = fields.Char(string='Order Number', readonly=True)
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Base', required=True)
    supervisor_id = fields.Many2one(
        'hr.employee',
        string='Supervisor',
        domain=[('mechanic', '=', True)],)
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now)
    current_odometer = fields.Float()
    type = fields.Selection(
        [('preventive', 'Preventive'),
         ('corrective', 'Corrective')],
        required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        default=lambda self: self._default_warehouse_id(),)
    start_date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        string='Schedule start')
    end_date = fields.Datetime(
        required=True,
        compute='_compute_end_date',
        string='Schedule end'
    )
    start_date_real = fields.Datetime(
        readonly=True,
        string='Real start date')
    end_date_real = fields.Datetime(
        compute="_compute_end_date_real",
        readonly=True,
        string='Real end date'
    )
    order_line_ids = fields.One2many(
        'vms.order.line',
        'order_id',
        string='Order Lines',
        ondelete="casacade",
    )
    program_id = fields.Many2one(
        'vms.program',
        string='Program')
    report_ids = fields.Many2many(
        'vms.report',
        string='Report(s)')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released'),
         ('cancel', 'Cancel')],
        readonly=True,
        default='draft')
    unit_id = fields.Many2one(
        'fleet.vehicle',
        string='Unit', required=True, store=True)
    picking_ids = fields.Many2many(
        'stock.picking',
        compute='_compute_picking_ids',
        string='Stock Pickings',
        copy=False,)
    pickings_count = fields.Integer(
        string='Delivery Orders',
        compute='_compute_pickings_count',
        copy=False,)
    procurement_group_id = fields.Many2one(
        'procurement.group',
        string='Procurement Group',
        readonly=True,
        copy=False,)

    @api.multi
    @api.depends('procurement_group_id')
    def _compute_picking_ids(self):
        for rec in self:
            rec.picking_ids = (
                self.env['stock.picking'].search(
                    [('group_id', '=', rec.procurement_group_id.id)])
                if rec.procurement_group_id else [])

    @api.multi
    @api.depends('picking_ids')
    def _compute_pickings_count(self):
        for rec in self:
            rec.pickings_count = (
                self.env['stock.picking'].search_count(
                    [('group_id', '=', rec.procurement_group_id.id)])
                if rec.procurement_group_id else 0)

    @api.multi
    def action_view_pickings(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.model
    def create(self, values):
        res = super(VmsOrder, self).create(values)
        if res.operating_unit_id.order_sequence_id:
            sequence = res.operating_unit_id.order_sequence_id
            res.name = sequence.next_by_id()
        else:
            raise ValidationError(_(
                'Verify that the sequences in the base are assigned'))
        return res

    @api.depends('order_line_ids')
    def _compute_end_date_real(self):
        for rec in self:
            if rec.start_date_real:
                sum_time = 0.0
                for line in rec.order_line_ids:
                    if line.state == 'done':
                        sum_time += line.real_duration
                strp_date = fields.Datetime.from_string(rec.start_date_real)
                rec.end_date_real = strp_date + timedelta(hours=sum_time)

    @api.multi
    def action_released(self):
        for order in self:
            for line in order.order_line_ids:
                line.action_done()
            # if order.type == 'preventive':
                # Preguntar que tenemos que hacer ahora.
            if order.type == 'corrective':
                for report in order.report_ids:
                    report.state = 'closed'
            order.state = 'released'

    @api.multi
    def get_tasks_from_cycle(self, cycle_id, order_id):
        spares = []
        for cycle in cycle_id:
            for task in cycle.task_ids:
                duration = task.duration
                start_date = fields.Datetime.from_string(fields.Datetime.now())
                end_date = start_date + timedelta(
                    hours=duration)
                for spare_part in task.spare_part_ids:
                    spares.append((0, False, {
                        'product_id': spare_part.product_id.id,
                        'product_qty': spare_part.product_qty,
                        'product_uom_id': (
                            spare_part.product_uom_id.id),
                        'state': 'draft'
                    }))
                order_id.order_line_ids += order_id.order_line_ids.new({
                    'task_id': task.id,
                    'start_date': start_date,
                    'duration': duration,
                    'end_date': end_date,
                    'spare_part_ids': [line for line in spares],
                    'order_id': order_id.id
                })
            if cycle.cycle_ids:
                for sub_cycle in cycle.cycle_ids:
                    order_id.get_tasks_from_cycle(
                        sub_cycle, order_id)
            else:
                break

    @api.onchange('type', 'unit_id')
    def _onchange_type(self):
        if self.type == 'preventive':
            self.program_id = self.unit_id.program_id
            self.current_odometer = self.unit_id.odometer
            for cycle in self.program_id.cycle_ids:
                self.get_tasks_from_cycle(cycle, self)
        else:
            self.program_id = False
            self.current_odometer = False
            self.order_line_ids = False

    @api.depends('order_line_ids')
    def _compute_end_date(self):
        for rec in self:
            sum_time = 0.0
            if rec.start_date:
                for line in rec.order_line_ids:
                    sum_time += line.duration
                strp_date = fields.Datetime.from_string(rec.start_date)
                rec.end_date = strp_date + timedelta(hours=sum_time)

    @api.multi
    def action_open(self):
        for rec in self:
            orders = self.search_count([
                ('unit_id', '=', rec.unit_id.id), ('state', '=', 'open'),
                ('id', '!=', rec.id)])
            if orders > 0:
                raise ValidationError(_(
                    'Unit not available for maintenance because it has more '
                    'open order.'))
            if not rec.order_line_ids:
                raise ValidationError(_(
                    'The order must have at least one task'))
            rec.state = 'open'
            if rec.type == 'corrective':
                rec.report_ids.write({'state': 'pending'})
            rec.order_line_ids.action_process()
            rec.start_date_real = fields.Datetime.now()

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.order_line_ids.action_cancel()
            if rec.type == 'corrective':
                rec.report_ids.write({'state': 'pending', })
            rec.state = 'cancel'

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'
            if rec.type == 'corrective':
                rec.report_ids.write({'state': 'pending', })
            rec.order_line_ids.write({'state': 'draft', })

    def _prepare_procurement_group(self):
        return {
            'name': self.name,
            'move_type': 'direct',
        }

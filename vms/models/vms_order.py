# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, fields, models
from datetime import datetime, timedelta


class VmsOrder(models.Model):
    _description = 'VMS Orders'
    _inherit = 'mail.thread'
    _name = 'vms.order'

    name = fields.Char(string='Order Number', readonly=True)
    base_id = fields.Many2one(
        'tms.base', string='Base', required=True)
    supervisor_id = fields.Many2one(
        'hr.employee',
        required=True,
        domain=[('mechanic', '=', True)],
        string='Supervisor')
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now)
    current_odometer = fields.Float()
    type = fields.Selection(
        [('preventive', 'Preventive'),
         ('corrective', 'Corrective')],
        required=True)
    stock_location_id = fields.Many2one(
        'stock.location',
        domain="[('usage', '=', 'internal')]",
        required=True,
        string='Stock Location')
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
        store=True)
    program_id = fields.Many2one(
        'vms.program',
        string='Program')
    cycle_id = fields.Many2one(
        'vms.vehicle.cycle',
        string='Cycle')
    sequence = fields.Integer()
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

    @api.model
    def create(self, values):
        order = super(VmsOrder, self).create(values)
        sequence = order.base_id.order_sequence_id
        order.name = sequence.next_by_id()
        return order

    @api.depends('order_line_ids')
    def _compute_end_date_real(self):
        for rec in self:
            if rec.start_date_real:
                sum_time = 0.0
                for line in rec.order_line_ids:
                    if line.state == 'done':
                        sum_time += line.real_duration
                strp_date = datetime.strptime(
                    rec.start_date_real, "%Y-%m-%d %H:%M:%S")
                rec.end_date_real = strp_date + timedelta(hours=sum_time)

    @api.multi
    def action_released(self):
        for order in self:
            if order.type == 'preventive':
                for line in order.order_line_ids:
                    if line.state != 'done':
                        raise exceptions.ValidationError(
                            'Verify that all activities are in '
                            'end state to continue')
                cycles = order.unit_id.cycle_ids.search(
                    [('sequence', '=', order.unit_id.sequence),
                     ('unit_id', '=', order.unit_id.id)])
                cycles.write({
                    'order_id': order.id,
                    'date': fields.Datetime.now(),
                    'distance': order.current_odometer
                })
                order.unit_id.last_order_id = order.id
                order.unit_id.last_cycle_id = order.cycle_id.id
                order.unit_id.next_service_odometer = cycles.schedule
                order.unit_id.sequence += 1
                next_cycle = order.unit_id.cycle_ids.search(
                    [('sequence', '=', order.unit_id.sequence),
                     ('unit_id', '=', order.unit_id.id)])
                order.unit_id.write({'next_cycle_id': next_cycle.id})
            elif order.type == 'corrective':
                for report in order.report_ids:
                    if report.state == 'confirmed':
                        report.state = 'close'
                    else:
                        raise exceptions.ValidationError(
                            'Verify that all reports are in '
                            'confirm state to continue')
            order.state = 'released'
            order.message_post(body=(
                "<h5><strong>Released</strong></h5>"
                "<p><strong>Released by: </strong> %s <br>"
                "<strong>Released at: </strong> %s</p") % (
                order.supervisor_id.name, fields.Datetime.now()))

    @api.multi
    @api.onchange('type', 'unit_id')
    def _onchange_type(self):
        for rec in self:
            if (rec.type == 'preventive'):
                spares = []
                rec.program_id = rec.unit_id.program_id
                rec.current_odometer = rec.unit_id.odometer
                rec.sequence = rec.unit_id.sequence
                for cycle in rec.unit_id.next_cycle_id:
                    rec.cycle_id = cycle.id

                for task in rec.cycle_id.cycle_id.task_ids:
                    duration = task.duration
                    start_date = datetime.now()
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
                    order_line = rec.order_line_ids.create({
                        'task_id': task.id,
                        'start_date': start_date,
                        'duration': duration,
                        'end_date': end_date,
                        'spare_part_ids': [line for line in spares],
                        'order_id': rec.id
                        })
                    rec.order_line_ids += order_line
            else:
                rec.program_id = False
                rec.current_odometer = False
                rec.sequence = False
                rec.order_line_ids = False

    @api.depends('order_line_ids')
    def _compute_end_date(self):
        for rec in self:
            sum_time = 0.0
            for line in rec.order_line_ids:
                sum_time += line.duration
            strp_date = datetime.strptime(rec.start_date, "%Y-%m-%d %H:%M:%S")
            rec.end_date = strp_date + timedelta(hours=sum_time)

    @api.multi
    def action_open(self):
        for rec in self:
            orders = self.search_count(
                [('unit_id', '=', rec.unit_id.id),
                 ('state', '!=', 'released'),
                 ('id', '!=', rec.id)])
            if orders > 0:
                raise exceptions.ValidationError(_(
                    'Unit not available for maintenance '
                    'because it has more open order(s).'))
            else:
                if not rec.order_line_ids:
                    raise exceptions.ValidationError(
                        _('The order must have at least one task'))
                for line in rec.order_line_ids:
                    if not line.external:
                        if line.responsible_ids:
                            obj_activity = self.env['vms.activity']
                            activities = obj_activity.search(
                                [('order_line_id', '=', line.id)])
                            if len(activities) > 0:
                                for activity in activities:
                                    activity.state = 'draft'
                            else:
                                for mechanic in line.responsible_ids:
                                    obj_activity.create({
                                        'order_id': rec.id,
                                        'task_id': line.task_id.id,
                                        'name': line.task_id.name,
                                        'unit_id': rec.unit_id.id,
                                        'order_line_id': line.id,
                                        'responsible_id': mechanic.id
                                        })
                            if(line.spare_part_ids):
                                for product in line.spare_part_ids:
                                    product.state = 'open'
                            if rec.type == 'corrective':
                                for report in rec.report_ids:
                                    report.state = 'open'
                        else:
                            raise exceptions.ValidationError(
                                _('The tasks must have almost one mechanic.'))

                    line.state = 'process'
                    line.start_date_real = fields.Datetime.now()
                    rec.state = 'open'
                    rec.start_date_real = fields.Datetime.now()
                    rec.message_post(_(
                        '<strong>Order Opened.</strong><ul>'
                        '<li><strong>Opened by: </strong>%s</li>'
                        '<li><strong>Opened at: </strong>%s</li>'
                        '</ul>') % (
                        self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_cancel(self):
        for rec in self:
            for line in rec.order_line_ids:
                line.action_cancel()
            if rec.type == 'corrective':
                for report in rec.report_ids:
                    report.state = 'cancel'
            rec.state = 'cancel'
            rec.message_post(_(
                '<strong>Order Closed.</strong><ul>'
                '<li><strong>Closed by: </strong>%s</li>'
                '<li><strong>Closed at: </strong>%s</li>'
                '</ul>') % (
                self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'
        if rec.type == 'corrective':
            for report in rec.report_ids:
                report.state = 'draft'
        for line in rec.order_line_ids:
            line.state = 'draft'
            for spare in line.spare_part_ids:
                spare.state = 'draft'

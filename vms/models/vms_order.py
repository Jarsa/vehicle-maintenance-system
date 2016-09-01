# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, fields, models


class VmsOrder(models.Model):
    _description = 'VMS Orders'
    _inherit = 'mail.thread'
    _name = 'vms.order'

    name = fields.Char(string='Order Number', readonly=True)
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
        # compute= '_compute_end_date'
        string='Schedule end'
        )
    start_date_real = fields.Datetime(
        readonly=True,
        string='Real start date')
    end_date_real = fields.Datetime(
        readonly=True,
        string='Real end date'
        )
    order_line_ids = fields.One2many(
        'vms.order.line',
        'order_id',
        string='Order Lines')
    program_id = fields.Many2one(
        'vms.program',
        string='Program')
    cycle_id = fields.Many2one(
        'vms.cycle',
        string='Cycle')
    sequence = fields.Integer()
    report_ids = fields.Many2many(
        'vms.report',
        domain=[('state', '=', 'confirmed')],
        string='Report(s)')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released')],
        readonly=True,
        default='draft')
    unit_id = fields.Many2one('fleet.vehicle', string='Unit', required=True)

    @api.model
    def create(self, values):
        order = super(VmsOrder, self).create(values)
        order.sequence = (len(self.search([])))
        return order

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        for rec in self:
            order = self.search([('unit_id', '=', rec.unit_id.id)])
            for vehicle in order:
                if vehicle.state != 'released':
                    raise exceptions.ValidationError(_(
                        'Unit not available because it has more'
                        'open order(s).'))

    @api.onchange('order_line_ids')
    def onchange_order_line(self):
        for order in self:
            if len(order.order_line_ids) > 0:
                if (len(order.order_line_ids.responsible_ids) == 0 and
                        not order.order_line_ids.external):
                    raise exceptions.ValidationError(
                        'Order Line must have at least one mechanical')

    @api.multi
    def action_open(self):
        for rec in self:
            obj_activity = self.env['vms.activity']
            for line in rec.order_line_ids:
                for mechanic in line.responsible_ids:
                    obj_activity.create({
                        'order_id': rec.id,
                        'task_id': line.task_id.id,
                        'name': line.task_id.name,
                        'unit_id': rec.unit_id.id,
                        'order_line_id': line.id,
                        'responsible_id': mechanic.id
                        })
                line.state = 'process'
                if(line.spare_part_ids):
                    for product in line.spare_part_ids:
                        product.state = 'open'
            rec.state = 'open'
            rec.message_post(_(
                '<strong>Order Opened.</strong><ul>'
                '<li><strong>Opened by: </strong>%s</li>'
                '<li><strong>Opened at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

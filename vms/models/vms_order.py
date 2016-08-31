# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, exceptions, fields, models


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
        string='State',
        readonly=True, default='draft')
    unit_id = fields.Many2one('fleet.vehicle', string='Unit', required=True)

    @api.multi
    def action_released(self):
        for order in self:
            activitys = self.env['vms.activity'].search(
                [('order_id', '=', order.id)])

            for activity in activitys:
                for line in order.order_line_ids:
                    if (activity.state is 'end' and
                            activity.order_line_id is line.id):
                        line.state = 'done'
                    else:
                        raise exceptions.ValidationError(
                            'Verify that all activities are in '
                            'end state to continue')
                order.message_post(body=(
                    "<h5><strong>Released</strong></h5>"
                    "<p><strong>Released by: </strong> %s <br>"
                    "<strong>Released at: </strong> %s</p") % (
                    order.supervisor_id.name, fields.Datetime.now()))

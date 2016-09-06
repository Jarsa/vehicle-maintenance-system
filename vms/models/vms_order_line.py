# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from datetime import timedelta
from openerp import _, api, exceptions, fields, models


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
        required=True,
        store=True)
    start_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    end_date_real = fields.Datetime(
        string='Real end date', readonly=True)
    duration = fields.Float(store=True)
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)])
    external = fields.Boolean()
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        domain=[('type', '=', 'service'), ('purchase_ok', '=', True)])
    qty_product = fields.Float(string="Quantity", default="1.0")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel')])
    real_duration = fields.Float(readonly=True)
    spare_part_ids = fields.One2many(
        'vms.product.line',
        'order_line_id',
        string='Spare Parts',
        help='You must save the order to select the mechanic(s).')
    responsible_ids = fields.Many2many(
        'hr.employee',
        string='Mechanics',
        domain=[('mechanic', '=', True)])
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True)
    purchase_state = fields.Boolean(
        string="Purchase Order State Done",
        compute='_compute_purchase_state')

    order_id = fields.Many2one('vms.order', string='Order', readonly=True)
    real_time_total = fields.Integer()

    @api.multi
    def action_done(self):
        for rec in self:
            for product in rec.spare_part_ids:
                product.create_stock_picking(
                    rec.order_id.stock_location_id.id,
                    product.product_id.id,
                    product.product_qty,
                    product.product_uom_id.id)

    @api.onchange('task_id')
    def _onchange_task(self):
        for rec in self:
            rec.duration = rec.task_id.duration
            strp_date = datetime.strptime(rec.start_date, "%Y-%m-%d %H:%M:%S")
            rec.end_date = strp_date + timedelta(hours=rec.duration)
            for spare_part in rec.task_id.spare_part_ids:
                spare = rec.spare_part_ids.new({
                    'product_id': spare_part.product_id.id,
                    'product_qty': spare_part.product_qty,
                    'product_uom_id': spare_part.product_uom_id.id,
                    'state': 'draft'})
                rec.spare_part_ids += spare

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

    @api.depends('purchase_order_id')
    def _compute_purchase_state(self):
        for rec in self:
            rec.purchase_state = (rec.purchase_order_id.id and
                                  rec.purchase_order_id.state == 'done')

    @api.multi
    def action_process(self):
        for rec in self:
            if rec.order_id.state != 'open':
                raise exceptions.ValidationError(
                    _('The order must be open.'))
            else:
                if rec.responsible_ids and not rec.external:
                    activities = self.env['vms.activity'].search(
                        [('order_line_id', '=', rec.id)])
                    if len(activities) > 0:
                        for activity in activities:
                            activity.state = 'draft'
                    else:
                        for mechanic in rec.responsible_ids:
                            self.env['vms.activity'].create({
                                'order_id': rec.order_id.id,
                                'task_id': rec.task_id.id,
                                'name': rec.task_id.name,
                                'unit_id': rec.order_id.unit_id.id,
                                'order_line_id': rec.id,
                                'responsible_id': mechanic.id
                                })
                    rec.state = 'process'
                    rec.start_date_real = fields.Datetime.now()
                    if rec.spare_part_ids:
                        for product in rec.spare_part_ids:
                            product.state = 'open'
                    rec.state = 'process'
                else:
                    raise exceptions.ValidationError(
                        _('The tasks must have almost one mechanic.'))

    @api.multi
    def action_done(self):
        act_state_validator = True
        # spare_validator = True
        sum_time = 0.0
        for rec in self:
            activities = rec.env['vms.activity'].search(
                [('order_line_id', '=', rec.id)])
            for activity in activities:
                if activity.state != 'end':
                    act_state_validator = False
                elif activity.state == 'end':
                    sum_time += activity.total_hours
            if not act_state_validator:
                raise exceptions.ValidationError(
                    _('The activities of the mechanics(s) must be finished.'))
            # for spare in rec.spare_part_ids:
            #     if spare.state != 'released':
            #         spare_validator = False
            # if not spare_validator:
            #     raise exceptions.ValidationError(
            #         _('The spare parts must be delivered.'))
            rec.end_date_real = fields.Datetime.now()
            rec.real_duration = sum_time
            rec.state = 'done'

    @api.multi
    def action_cancel(self):
        for rec in self:
            if not rec.external:
                activities = rec.env['vms.activity'].search(
                    [('order_line_id', '=', rec.id)])
                if len(activities) > 0:
                    for activity in activities:
                        activity.state = 'cancel'
                for spare in rec.spare_part_ids:
                    spare.state = 'cancel'
                    if spare.stock_move_id:
                        spare.stock_move_id.state = 'cancel'
            else:
                rec.purchase_order_id.unlink()
                if rec.spare_part_ids:
                    for spare in rec.spare_part_ids:
                        if spare.stock_move_id:
                            spare.stock_move_id.state = 'cancel'
                        spare.state = 'cancel'
            rec.state = 'cancel'
            rec.start_date_real = False

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def create_po(self):
        "Returns draft PO"
        purchase_order_id = self.env['purchase.order'].create({
            'partner_id': self.supplier_id.id,
            'partner_ref': self.order_id.name,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_qty': self.qty_product,
                'date_planned': fields.Datetime.now(),
                'product_uom': self.product_id.uom_po_id.id,
                'price_unit': self.product_id.standard_price,
                'taxes_id': [(
                    6, 0,
                    [x.id for x in (
                        self.product_id.supplier_taxes_id)]
                    )],
                'name': self.product_id.name})]})
        self.write({'purchase_order_id': purchase_order_id.id})

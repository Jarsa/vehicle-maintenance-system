# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        store=True,
        readonly=True)
    start_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    end_date_real = fields.Datetime(
        string='Real Finishing', readonly=True)
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
        help='You must save the order to select the mechanic(s).',
        ondelete="cascade",)
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True)
    purchase_state = fields.Boolean(
        string="Purchase Order State Done",
        compute='_compute_purchase_state')
    order_id = fields.Many2one('vms.order', string='Order', readonly=True)
    real_time_total = fields.Integer()
    create_purchase_order = fields.Boolean(
        compute='_compute_create_purchase_order')

    @api.multi
    def unlink(self):
        self.spare_part_ids.unlink()
        return super(VmsOrderLine, self).unlink()

    @api.onchange('external')
    def _onchange_external(self):
        for rec in self:
            if rec.external:
                rec.spare_part_ids = False
            else:
                for spare_part in rec.task_id.spare_part_ids:
                    spare = rec.spare_part_ids.new({
                        'product_id': spare_part.product_id.id,
                        'product_qty': spare_part.product_qty,
                        'product_uom_id': spare_part.product_uom_id.id,
                        'state': 'draft'})
                    rec.spare_part_ids += spare

    @api.onchange('task_id')
    def _onchange_task(self):
        for rec in self:
            rec.duration = rec.task_id.duration
            rec.spare_part_ids = {}
            if rec.start_date:
                strp_date = fields.Datetime.from_string(rec.start_date)
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
        for rec in self:
            if rec.start_date:
                strp_date = fields.Datetime.from_string(rec.start_date)
                rec.end_date = strp_date + timedelta(hours=rec.duration)

    @api.depends('start_date_real', 'end_date_real')
    def _compute_real_time_total(self):
        for rec in self:
            start_date = fields.Datetime.from_string(rec.start_date_real)
            end_date = fields.Datetime.from_string(rec.end_date_real)
            total_days = end_date - start_date
            rec.real_time_total = total_days.days

    @api.depends('purchase_order_id')
    def _compute_purchase_state(self):
        for rec in self:
            rec.purchase_state = (
                rec.purchase_order_id.id and
                rec.purchase_order_id.state == 'done')

    @api.depends('spare_part_ids')
    def _compute_create_purchase_order(self):
        for rec in self:
            rec.create_purchase_order = bool(
                rec.spare_part_ids.filtered(
                    lambda x: x.external_spare_parts))

    @api.multi
    def action_process(self):
        for rec in self:
            if rec.order_id.state != 'open':
                raise ValidationError(_('The order must be open.'))
            rec.write({
                'state': 'process',
                'start_date_real': fields.Datetime.now(),
            })
            if not rec.external:
                if not rec.spare_part_ids:
                    return True
                rec.spare_part_ids.procurement_create()
        return True

    @api.multi
    def get_real_duration(self):
        for rec in self:
            rec.real_duration = sum([task.duration for task in rec.task_id])

    @api.multi
    def action_done(self):
        for rec in self:
            if rec.external:
                if not rec.purchase_state:
                    raise ValidationError(_(
                        'Verify that purchase order are in done state '
                        'to continue'))
            rec.get_real_duration()
            rec.end_date_real = fields.Datetime.now()
            rec.state = 'done'

    @api.multi
    def action_cancel(self):
        for rec in self:
            if not rec.external:
                # That is intended to validate with this code,
                # because vms.product.line has no status.
                # ----------------------------------------------
                # if self.mapped('spare_part_ids').filtered(
                #         lambda x: x.state == 'done'):
                #     raise ValidationError(
                #         _('Error, you cannot cancel a maintenance order'
                #             ' with done stock moves.'))
                self.mapped('spare_part_ids').mapped(
                    'procurement_ids').cancel()
            rec.write({
                'state': 'cancel',
                'start_date_real': False,
            })

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _prepare_item(self, line):
        return {
            'product_id': line.product_id.id,
            'product_qty': line.product_qty,
            'date_planned': fields.Datetime.now(),
            'product_uom': line.product_id.uom_po_id.id,
            'price_unit': line.product_id.standard_price,
            'taxes_id': [(
                6, 0,
                [x.id for x in (
                    line.product_id.supplier_taxes_id)]
            )],
            'name': line.product_id.name
        }

    @api.multi
    def create_po(self):
        items = []
        items.append((0, 0, {
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
            'name': self.product_id.name
        }))
        lines = self.spare_part_ids.filtered(lambda r: r.external_spare_parts)
        if lines:
            for line in lines:
                items.append((0, 0, self._prepare_item(line)))
        purchase_order_id = self.env['purchase.order'].create({
            'partner_id': self.supplier_id.id,
            'partner_ref': self.order_id.name,
            'order_line': items,
            'picking_type_id': self.env.ref(
                'vms.stock_picking_type_vms_in').id,
        })
        self.write({'purchase_order_id': purchase_order_id.id})
        return {
            'name': 'Purchase Order',
            'view_id': self.env.ref(
                'purchase.purchase_order_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order_id.id,
            'type': 'ir.actions.act_window'
        }
